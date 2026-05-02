from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            f"{user.pk}{timestamp}{user.password}{user.is_active}{user.is_first_login}"
        )


activation_token_generator = ActivationTokenGenerator()
