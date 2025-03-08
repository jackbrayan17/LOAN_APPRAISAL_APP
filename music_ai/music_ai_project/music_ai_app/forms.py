from django import forms

GENRE_CHOICES = [
    ('pop', 'Pop'),
    ('rock', 'Rock'),
    ('hiphop', 'Hip Hop'),
    ('jazz', 'Jazz'),
    ('classical', 'Classical'),
    ('electronic', 'Electronic'),
    ('afrobeats', 'Afrobeats'),  # Added Afrobeats
]

class ImageUploadForm(forms.Form):
    image = forms.ImageField()
    genre = forms.MultipleChoiceField(
        choices=GENRE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
