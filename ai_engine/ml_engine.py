# ai_engine/ml_engine.py
import numpy as np
import pandas as pd
import joblib
import hashlib
import traceback
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Dense, Dropout # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
from django.core.cache import cache
from django.db.models import Count, Avg, Case, When, FloatField, Q
from django.contrib.auth import get_user_model
from ai_engine.models import AIEngine
from courses.models import Course, StudentAnswer, Progress, StudentCourse

# Workaround for TensorFlow compatibility
if not hasattr(np, '_ARRAY_API'):
    np._ARRAY_API = np.__dict__

class LearningPathRecommender:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.feature_columns = [
            'topic_completion', 
            'assignment_score', 
            'correct_ratio', 
            'course_category'
        ]
        
    def _get_training_data(self):
        """Collect and prepare training data from database"""
        User = get_user_model()
        
        # Get students with their performance metrics
        students = User.objects.filter(role='student').annotate(
            completed_courses=Count(
                'course_enrollments__progress', 
                filter=Q(course_enrollments__progress__percentage=100)
            ),
            avg_score=Avg(
                Case(
                    When(submissions__answers__is_correct=True, then=1.0),
                    default=0.0,
                    output_field=FloatField()
                )
            )
        )
        
        # Build feature matrix
        data = []
        for student in students:
            # Get progress data
            progress_data = Progress.objects.filter(
                enrollment__student=student
            ).aggregate(avg_completion=Avg('percentage'))
            
            # Get most relevant course category
            course_data = StudentCourse.objects.filter(
                student=student
            ).values('course__category').annotate(
                topic_completion=Avg('progress__percentage')
            ).order_by('-topic_completion').first()
            
            # Calculate correctness ratio
            correctness = StudentAnswer.objects.filter(
                submission__student=student
            ).aggregate(
                ratio=Avg(
                    Case(
                        When(is_correct=True, then=1.0),
                        default=0.0,
                        output_field=FloatField()
                    )
                )
            )['ratio'] or 0
            
            data.append({
                'student_id': student.id,
                'topic_completion': progress_data['avg_completion'] or 0,
                'assignment_score': student.avg_score or 0,
                'correct_ratio': correctness,
                'course_category': course_data['course__category'] if course_data else 'beginner'
            })
            
        return pd.DataFrame(data)

    def _build_keras_model(self, input_dim):
        """Build neural network model"""
        model = Sequential([
            Dense(128, activation='relu', input_shape=(input_dim,)),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(
            optimizer=Adam(0.001), 
            loss='binary_crossentropy', 
            metrics=['accuracy']
        )
        return model

    def _generate_synthetic_data(self):
        """Create balanced synthetic training data"""
        categories = [c[0] for c in Course.CATEGORY_CHOICES]
        synthetic = []
        
        for i, category in enumerate(categories):
            synthetic.append({
                'student_id': -i-1,  # Negative IDs for synthetic
                'topic_completion': (i+1)*25,
                'assignment_score': 0.2 + (i*0.3),
                'correct_ratio': 0.3 + (i*0.2),
                'course_category': category
            })
        return pd.DataFrame(synthetic)

    def _create_fallback_model(self):
        """Create simple model when training fails"""
        model = DummyClassifier(strategy='stratified')
        model.fit([[0,0,0]], [0])  # Minimal dummy data
        
        model_hash = hashlib.sha256(b'fallback').hexdigest()
        joblib.dump(model, f'ai_models/{model_hash}.joblib')
        
        AIEngine.objects.update(is_active=False)
        AIEngine.objects.create(
            version='FALLBACK',
            accuracy=0.0,
            training_logs="Fallback model - insufficient categories"
        )
        return 0.0

    def train(self):
        """Train the recommendation model"""
        try:
            df = self._get_training_data()
            df.to_csv(f"ai_models/training_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv", index=False)
            
            # Validate we have multiple categories
            unique_categories = df['course_category'].unique().tolist()
            if len(unique_categories) < 2:
                synthetic_data = self._generate_synthetic_data()
                df = pd.concat([df, synthetic_data], ignore_index=True)
                unique_categories = df['course_category'].unique().tolist()

            if len(unique_categories) < 2:
                return self._create_fallback_model()
            
            # Prepare features and target
            X = df.drop(['student_id', 'course_category'], axis=1)
            y = df['course_category'].factorize()[0]

            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Build preprocessing pipeline
            preprocessor = ColumnTransformer([
                ('num', StandardScaler(), ['topic_completion', 'assignment_score', 'correct_ratio'])
            ])
            
            # Create model pipeline
            model = Pipeline([
                ('preprocessor', preprocessor),
                ('classifier', GradientBoostingClassifier(
                    n_estimators=100,
                    random_state=42
                ))
            ])
            
            # Train and evaluate
            model.fit(X_train, y_train)
            test_acc = model.score(X_test, y_test)
            
            # Save models
            model_hash = hashlib.sha256(pd.util.hash_pandas_object(df).values).hexdigest()
            joblib.dump(model, f'ai_models/{model_hash}.joblib')
            
            keras_model = self._build_keras_model(X_train.shape[1])
            keras_model.save(f'ai_models/keras_{model_hash}.keras')
            
            # Update active model
            AIEngine.objects.update(is_active=False)
            AIEngine.objects.create(
                version=model_hash[:7],
                accuracy=test_acc,
                training_logs=f"Training accuracy: {test_acc:.2f}"
            )
            
            return test_acc
            
        except Exception as e:
            print(f"Training failed: {str(e)}")
            print(traceback.format_exc())
            return self._create_fallback_model()

    def recommend_for_student(self, student):
        """Get personalized course recommendations"""
        cache_key = f"recommendations_{student.id}"
        if cached := cache.get(cache_key):
            return cached
            
        # Load active model
        if not (current_model := AIEngine.objects.filter(is_active=True).first()):
            return self._get_fallback_recommendations()
            
        try:
            model = joblib.load(f'ai_models/{current_model.version}.joblib')
            
            # Get student data
            student_data = self._get_training_data().query(f"student_id == {student.id}")
            if student_data.empty:
                return self._get_fallback_recommendations()
                
            # Make prediction
            prediction = model.predict(student_data)
            
            # Get recommended courses
            recommendations = Course.objects.filter(
                category=prediction[0]
            ).exclude(
                enrollments__student=student
            ).annotate(
                similarity=Count('topics')
            ).order_by('-similarity')[:5]
            
            # Cache results
            cache.set(cache_key, recommendations, 60*60*6)  # 6 hours
            return recommendations
            
        except Exception as e:
            print(f"Recommendation failed: {str(e)}")
            return self._get_fallback_recommendations()

    def _get_fallback_recommendations(self):
        """Default recommendations when model fails"""
        return Course.objects.annotate(
            enroll_count=Count('enrollments')
        ).order_by('-enroll_count')[:5]