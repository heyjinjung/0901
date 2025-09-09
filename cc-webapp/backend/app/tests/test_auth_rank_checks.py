from app.services.auth_service import AuthService


def test_combined_access_rank_and_segment():
	# Requires at least PREMIUM and segment level >= 2
	assert AuthService.check_combined_access("VIP", 3, "PREMIUM", 2) is True
	assert AuthService.check_combined_access("PREMIUM", 2, "PREMIUM", 2) is True
	assert AuthService.check_combined_access("STANDARD", 5, "PREMIUM", 2) is False
	assert AuthService.check_combined_access("VIP", 1, "PREMIUM", 2) is False
