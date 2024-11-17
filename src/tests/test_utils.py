import pytest

from platzi.utils import clean_string, get_course_slug, slugify


def test_get_course_slug():
    valid_url = "https://platzi.com/cursos/fastapi-2023/"
    assert get_course_slug(valid_url) == "fastapi-2023"
    invalid_url = "https://platzi.com/home/clases/9012-fastapi-2023/"
    with pytest.raises(Exception):
        get_course_slug(invalid_url)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Hello, World!", "Hello World"),
        ("   1234:;<>?{}|", "1234"),
        ("Café! Frío?", "Café Frío"),
        ("º~ª Special chars: @#$%^&*()!", "Special chars"),
    ],
)
def test_clean_string(text, expected):
    assert clean_string(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Hello, World!", "hello-world"),
        ("   1234:;<>?{}|", "1234"),
        ("Café! Frío?", "cafe-frio"),
        ("º~ª Special chars: @#$%^&*()!", "special-chars"),
    ],
)
def test_slugify(text, expected):
    assert slugify(text) == expected
