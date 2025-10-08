import random

import pytest
from faker import Faker

from product.models import Feedback, Like

faker = Faker()


@pytest.fixture
def sample_feedbacks(
    db,
    sample_active_user,
    sample_products,
):
    def create_feedback(
        user=None,
        product=None,
        **kwargs,
    ):
        user = sample_active_user
        product = sample_products["products"][0]

        return Feedback.objects.create(
            user=user,
            product=product,
            description=kwargs.get("description", faker.text(max_nb_chars=100)),
            rating=kwargs.get("rating", random.randint(1, 5)),
        )

    return create_feedback


@pytest.fixture
def sample_likes(
    db,
):
    def create_favorites(user, product):
        return Like.objects.create(
            user=user,
            product=product,
        )

    return create_favorites
