from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Movie, Review


class ReportReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reporter', password='password')
        self.author = User.objects.create_user(username='author', password='password')
        self.movie = Movie.objects.create(
            name='Test Movie',
            price=10,
            description='Test description',
            image='movie_images/test.jpg',
        )
        self.review_to_report = Review.objects.create(
            comment='Inappropriate review', movie=self.movie, user=self.author
        )
        self.other_review = Review.objects.create(
            comment='Review that should remain', movie=self.movie, user=self.user
        )
        self.report_url = reverse(
            'movies.report_review',
            kwargs={'id': self.movie.id, 'review_id': self.review_to_report.id},
        )

    def test_report_review_deletes_only_selected_review_and_redirects(self):
        self.client.login(username='reporter', password='password')

        response = self.client.post(self.report_url)

        self.assertRedirects(response, reverse('movies.show', kwargs={'id': self.movie.id}))
        self.assertFalse(Review.objects.filter(id=self.review_to_report.id).exists())
        self.assertTrue(Review.objects.filter(id=self.other_review.id).exists())

        refreshed_page = self.client.get(reverse('movies.show', kwargs={'id': self.movie.id}))
        self.assertNotContains(refreshed_page, 'Inappropriate review')
        self.assertContains(refreshed_page, 'Review that should remain')

    def test_report_review_rejects_get_requests(self):
        self.client.login(username='reporter', password='password')

        response = self.client.get(self.report_url)

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Review.objects.filter(id=self.review_to_report.id).exists())

    def test_report_review_requires_authentication(self):
        response = self.client.post(self.report_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts.login'), response.url)
        self.assertTrue(Review.objects.filter(id=self.review_to_report.id).exists())

    def test_report_review_must_belong_to_movie_in_url(self):
        another_movie = Movie.objects.create(
            name='Another Movie',
            price=12,
            description='Another description',
            image='movie_images/another-test.jpg',
        )
        mismatched_url = reverse(
            'movies.report_review',
            kwargs={'id': another_movie.id, 'review_id': self.review_to_report.id},
        )
        self.client.login(username='reporter', password='password')

        response = self.client.post(mismatched_url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(id=self.review_to_report.id).exists())

    def test_existing_create_edit_and_delete_review_flow_still_works(self):
        self.client.login(username='reporter', password='password')

        self.client.post(
            reverse('movies.create_review', kwargs={'id': self.movie.id}),
            {'comment': 'New review'},
        )
        review = Review.objects.get(comment='New review')

        self.client.post(
            reverse(
                'movies.edit_review',
                kwargs={'id': self.movie.id, 'review_id': review.id},
            ),
            {'comment': 'Updated review'},
        )
        review.refresh_from_db()
        self.assertEqual(review.comment, 'Updated review')

        self.client.get(
            reverse(
                'movies.delete_review',
                kwargs={'id': self.movie.id, 'review_id': review.id},
            )
        )
        self.assertFalse(Review.objects.filter(id=review.id).exists())
