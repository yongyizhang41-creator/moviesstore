from urllib import response

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Movie, Review
from cart.models import Item, Order

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


class AdminStatisticsTests(TestCase):
    def setUp(self):
        self.url = reverse('movies.admin_statistics')
        self.regular_user = User.objects.create_user(
            username='regular-user', 
            password='password',
        )
        self.staff_user = User.objects.create_user(
            username='staff-user', 
            password='password', 
            is_staff=True,
        )

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse('accounts.login'),
            response.headers['Location'],
        )

    def test_regular_user_redirected_to_login(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse('accounts.login'),
            response.headers['Location'],
        )

    def test_staff_user_can_view_statistics_page(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'movies/admin_statistics.html',
        )

    def test_page_shows_different_purchase_and_review_winners(self):
        reviewed_movie = Movie.objects.create(
            name='Review Champion',
            price=10,
            description='Test description',
            image='movie_images/reviewed.jpg',
        )
        purchased_movie = Movie.objects.create(
            name='Purchase Champion',
            price=10,
            description='Test description',
            image='movie_images/purchased.jpg',
        )

        Review.objects.create(
            comment='Test review',
            movie=reviewed_movie,
            user=self.regular_user,
        )

        order = Order.objects.create(
            total=30,
            user=self.regular_user,
        )
        Item.objects.create(
            price=reviewed_movie.price,
            quantity=1,
            order=order,
            movie=reviewed_movie,
        )
        Item.objects.create(
            price=purchased_movie.price,
            quantity=2,
            order=order,
            movie=purchased_movie,
        )

        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)

        self.assertContains(response, 'Review Champion')
        self.assertContains(response, 'Purchase Champion')
        self.assertContains(response, '<strong>1</strong>', html=True)
        self.assertContains(response, '<strong>2</strong>', html=True)

    def test_same_movie_is_displayed_for_both_measurements(self):
        movie = Movie.objects.create(
            name='Champion Movie',
            price=10,
            description='Test description',
            image='movie_images/double-winner.jpg',
        )

        Review.objects.create(
            comment='Test review',
            movie=movie,
            user=self.regular_user,
        )

        order = Order.objects.create(
            total=30,
            user=self.regular_user,
        )
        Item.objects.create(
            price=movie.price,
            quantity=3,
            order=order,
            movie=movie,
        )

        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)

        self.assertContains(response, 'Champion Movie', count=2)
        self.assertContains(response, '<strong>3</strong>', html=True)
        self.assertContains(response, '<strong>1</strong>', html=True)

    def test_page_shows_message_when_there_is_no_activity(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)

        self.assertContains(
            response, 
            'No movies have been purchased yet',
        )
        self.assertContains(
            response, 
            'No movies have been reviewed yet',
        )

    def test_navigation_link_visible_only_to_staff(self):
        home_url = reverse('home.index')
        self.client.force_login(self.regular_user)
        regular_response = self.client.get(home_url)
        self.assertNotContains(
            regular_response, 
            'Movie Statistics',
        )
        self.client.logout()
        self.client.force_login(self.staff_user)
        staff_response = self.client.get(home_url)
        self.assertContains(
            staff_response, 
            'Movie Statistics',
        )