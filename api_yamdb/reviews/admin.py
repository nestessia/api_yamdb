from django.contrib import admin

from reviews.models import Comments, Review, Title, Genre, Category, TitleGenre
from users.users import User


admin.site.register(Title)
admin.site.register(Comments)
admin.site.register(Review)
admin.site.register(TitleGenre)
admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Category)
