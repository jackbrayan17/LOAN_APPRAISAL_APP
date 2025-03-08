from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .forms import ImageUploadForm
from .ocr_utils import extract_text_from_image
from .spotify_utils import search_songs

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            genres = form.cleaned_data['genre']  # Get selected genres

            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            extracted_text = extract_text_from_image(fs.path(filename))

            # Combine multiple genres into a query-friendly format
            genre_query = " OR ".join(genres)

            daily_songs = {title: search_songs(title, genre_query) for title in extracted_text if title}

            return render(request, 'music_ai_app/results.html', {'daily_songs': daily_songs})
    else:
        form = ImageUploadForm()

    return render(request, 'music_ai_app/upload.html', {'form': form})
