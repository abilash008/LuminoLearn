# ai_engine/management/commands/train_model.py
import hashlib
from django.core.management.base import BaseCommand
import pandas as pd
from ai_engine.ml_engine import LearningPathRecommender
from ai_engine.models import AIEngine as AIModel
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Train the recommendation model and update active version'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force training even if no new data exists'
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting model training...")
        
        # Check if training is needed
        if not options['force']:
            latest_model = AIModel.objects.order_by('-trained_at').first()
            if latest_model and latest_model.training_data_hash == self.current_data_hash():
                self.stdout.write("✅ No new data - skipping training")
                return

        try:
            recommender = LearningPathRecommender()
            accuracy = recommender.train()
            
            self.stdout.write(self.style.SUCCESS(
                f"Model trained successfully! Accuracy: {accuracy:.2f}"
            ))
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            self.stderr.write(self.style.ERROR(
                f"Training failed: {str(e)}"
            ))

    def current_data_hash(self):
        # Generate hash of current training data
        recommender = LearningPathRecommender()
        df = recommender._get_training_data()
        return hashlib.md5(
        pd.util.hash_pandas_object(df).values.tobytes()).hexdigest()