# ai_engine/tasks.py
import logging
from celery import shared_task
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from .ml_engine import LearningPathRecommender
from .utils import send_slack_alert, send_email_to_admins
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def retrain_model(self, manual_trigger=False):
    """
    Retrains the ML model with enhanced tracking and versioning
    """
    try:
        logger.info(f"🚀 Starting model retraining (Attempt {self.request.retries + 1})")
        if manual_trigger:
            send_slack_alert("🔧 Manual model retraining initiated")

        # Get current model version from cache
        current_version = cache.get(settings.MODEL_VERSION_KEY, 0)
        new_version = current_version + 1
        
        recommender = LearningPathRecommender()
        accuracy, training_time = recommender.train()
        
        # Store model metadata
        model_metadata = {
            'version': new_version,
            'accuracy': float(accuracy),
            'training_time': training_time,
            'sample_count': recommender.training_samples,
            'features_used': recommender.feature_list,
        }
        cache.set(settings.MODEL_VERSION_KEY, new_version)
        cache.set(f"{settings.MODEL_VERSION_KEY}_{new_version}", model_metadata)
        
        logger.info(f"✅ Model v{new_version} trained successfully | Accuracy: {accuracy:.2f}")
        send_slack_alert(f"🤖 Model v{new_version} deployed | Accuracy: {accuracy:.2f}% | Time: {training_time:.1f}s")
        
        return model_metadata
        
    except Exception as e:
        logger.error(f"❌ Model retraining failed: {str(e)}")
        send_email_to_admins(
            subject="Model Training Failure",
            message=f"Error in retrain_model: {str(e)}"
        )
        self.retry(exc=e, countdown=30 * (self.request.retries + 1))

@shared_task(bind=True, max_retries=3)
def refresh_recommendations(self, precompute_active=True):
    """
    Enhanced cache refresh with precomputing for active users
    """
    try:
        User = get_user_model()
        logger.info("🔄 Starting recommendations refresh")
        
        # Get active students (last login within 30 days)
        active_students = User.objects.filter(
            role='student',
            last_login__gte=timezone.now() - timezone.timedelta(days=30)
        ).values_list('id', flat=True)
        
        # Batch processing with progress tracking
        total_users = active_students.count()
        BATCH_SIZE = settings.CACHE_BATCH_SIZE
        recommender = LearningPathRecommender()
        
        # Delete existing recommendations
        keys_to_delete = [f"recommendations_{uid}" for uid in active_students]
        for i in range(0, len(keys_to_delete), BATCH_SIZE):
            batch = keys_to_delete[i:i+BATCH_SIZE]
            cache.delete_many(batch)
            self.update_state(
                state='PROGRESS',
                meta={'current': i, 'total': total_users}
            )
        
        # Precompute recommendations for active users
        if precompute_active:
            logger.info("♻️ Precomputing recommendations for active users")
            for i, user_id in enumerate(active_students):
                recommendations = recommender.get_recommendations(user_id)
                cache.set(
                    f"recommendations_{user_id}",
                    recommendations,
                    timeout=settings.CACHE_TTL
                )
                if i % 500 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={'current': i, 'total': total_users}
                    )
        
        logger.info(f"✅ Recommendations refreshed for {total_users} users")
        return {"status": "complete", "users_processed": total_users}
        
    except Exception as e:
        logger.error(f"❌ Cache refresh failed: {str(e)}")
        self.retry(exc=e, countdown=60)

@shared_task
def system_health_check():
    """
    Comprehensive system health check task
    """
    checks = {
        'model_version': cache.get(settings.MODEL_VERSION_KEY, 0),
        'cache_available': cache.ping(),
        'recommendations_count': len(cache.keys('recommendations_*')),
        'last_training_time': cache.get(f"{settings.MODEL_VERSION_KEY}_current", {}).get('training_time', 0)
    }
    
    # Send alert if model is older than 7 days
    if checks['model_version'] == 0 or checks['last_training_time'] < (timezone.now() - timezone.timedelta(days=7)):
        send_slack_alert("⚠️ Model age alert: Model is older than 7 days")
    
    return checks

@shared_task
def emergency_cache_refresh(user_ids=None):
    """
    Priority task for emergency cache refresh
    """
    if user_ids:
        keys_to_refresh = [f"recommendations_{uid}" for uid in user_ids]
        cache.delete_many(keys_to_refresh)
        return f"Emergency refresh completed for {len(user_ids)} users"
    return "No users specified for emergency refresh"