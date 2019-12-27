## Goal

Create a freeware library to run translation of fields without need to 
restart the server, without changing model code, storing the translations
in database and ability to search all translations, current language or by
translations of a specify language.

### Problem

Existing solutions for their approach are divided into those who
store the translation in a separate column of the main table
and on those who store the translation in separate tables for 
each model. These approaches overlap the restriction is that
if you want to start to translate a new field or model you are making 
changes in the structure of the database and in consequence 
of what is necessary server restart. In parallel with this, 
the majority of decisions to make make changes to the model
code making it more difficult to understand.

### Solution

To solve the problems it is proposed to develop a Django application that
would allow to store in one table a reference to a field in the model, and in 
another - translations in a shared table with a static structure would not change
the standard scenario of using ORM fields and would not require
server restart.

### Usage scenario

~~~python
class Book(models.Model):
    title = models.CharField(_('Title'), max_length=250, default='', blank=True, null=False)
    active = models.BooleanField(_('active'), default=False)
    sort = models.IntegerField(_('sort'), default=0, blank=True, null=True)
    book = Book.objects.create(title='Title')
~~~
Then the title field is added to the table of translated fields
TranslatableFields. Programmatically or through the admin interface:

~~~python
fld = TranslatableFields.objects.create(
    name='title',
    content_type=ContentType.objects.get_for_model(Book),
)
~~~

And in the translation table added translation for the instance.
Programmatically or through the admin interface:

~~~python
Translations.objects.create(
    content_object=book,
    field=fld,
    lang=Language.objects.get('en'),
    value='en',
)
~~~

Then you can interact with model Book:

~~~python
from django.utils.translation import activate

activate('en')
book = Book.objects.first()
book.title  # => Title en
~~~
### Prototypes of interfaces:

In the first approximation of the interfaces you will need a widget for translatable
fields.

![Widget for translatable fields](https://github.com/mom1/django-tof/blob/master/docs/images/widget.png)

Where the tab with an active language are marked with a blue colour.

Not empty bookmarks are marked in dark.

Also, at the end of bookmarks, you need to add a bookmark with the + symbol by clicking
which opens the language selection dialog. The selected language appears as
bookmark.

### Terms

Main MVP should take no more then 2 mounth.

-  Working prototype no more then 1 month.

- Testing and documentation - 1 month.

- A pilot project - 1 month.


PACKAGE|Model code changing|Storage of translations|Need to restart the server to display the new translation|Changing the structure when adding a field as a translatable field
-------|-------------------|-----------------------|---------------------------------------------------------|------------------------------------------------------------------
DJANGO-MODELTRANSLATION|      -                    |Table fields of the translated model|       -           |                       +
DJANGO-HVAD|                  +                    |Separate table for each model|              -           |                       +
DJANGO-PARLER|                +                    |Separate table for each model|              -           |                       +
Default Django Translation|   -                    |.po files|                                  +           |                       -
