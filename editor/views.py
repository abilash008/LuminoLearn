

# views.py (updated for Piston API)
import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def code_editor(request):
    """
    Renders the code editor page with a list of supported languages.
    """
    supported_languages = [
        {'name': 'Python', 'value': 'python3'},
        {'name': 'JavaScript', 'value': 'nodejs'},
        {'name': 'Java', 'value': 'java'},
        {'name': 'C++', 'value': 'cpp'},
    ]
    return render(request, 'student/editor.html', {'languages': supported_languages})

@csrf_exempt
@login_required
def execute_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            code = data.get('code')
            frontend_lang = data.get('language', 'python3')
            user_input = data.get('input', '') + '\n'

            language_mapping = {
                'python3': {'piston_lang': 'python', 'version': '3.10.0'},
                'nodejs': {'piston_lang': 'javascript', 'version': '18.15.0'},
                'java': {'piston_lang': 'java', 'version': '15.0.2'},
                'cpp': {'piston_lang': 'cpp', 'version': '10.2.0'},
            }
            lang_info = language_mapping.get(frontend_lang, language_mapping['python3'])

            # Language-specific code modifications
            modified_code = code
            if lang_info['piston_lang'] == 'python':
                modified_code = code.replace('input(', 'print("\\x1B[INPUT]"); input(')
            elif lang_info['piston_lang'] == 'java':
                # Use proper Java Unicode escape sequence
                modified_code = code.replace(
                    'new Scanner(System.in);', 
                    'new Scanner(System.in); System.out.print("\\u001B[INPUT]");'
                )
                if 'public class Main' in modified_code and 'package' not in modified_code:
                    modified_code = f'package tmp;\n{modified_code}'
            elif lang_info['piston_lang'] == 'cpp':
                modified_code = code.replace('std::cin', 'std::cout << "\\x1B[INPUT]"; std::cin')

            payload = {
                "language": lang_info['piston_lang'],
                "version": lang_info['version'],
                "files": [{"content": modified_code}],
                "stdin": user_input
            }

            response = requests.post('https://emkc.org/api/v2/piston/execute', json=payload)
            response.raise_for_status()
            result = response.json()

            # Handle output and errors for different languages
            output = ''
            error = ''

            if lang_info['piston_lang'] in ['java', 'cpp']:
                # Combine compile and run outputs
                compile_output = result.get('compile', {}).get('output', '')
                run_output = result.get('run', {}).get('output', '')
                output = f"{compile_output}\n{run_output}".strip()
                error = result.get('compile', {}).get('stderr', '') or result.get('run', {}).get('stderr', '')
            else:
                # Interpreted languages
                output = result.get('run', {}).get('output', '')
                error = result.get('run', {}).get('stderr', '')

            # Format input prompts
            formatted_output = output.replace('Enter Your name:', '\x1B[INPUT]Enter Your name:')

            return JsonResponse({
                'output': formatted_output.strip(),
                'error': error.strip()
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'API Connection Error: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'Execution Error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
