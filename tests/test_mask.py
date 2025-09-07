from utils.mask import mask_email


def test_mask_email_basic():
    assert mask_email('verify@example.com') == 'ver***ify@*****.com'


def test_mask_email_short_local():
    assert mask_email('ab@domain.com', keep_prefix=1, keep_suffix=1) == 'a***b@*****.com'
