from django.db import models
from django.utils import timezone
from super_admin.models import Country, NoteCategory, NoteType
from authenticate.models import User

class SellerNotes(models.Model):
    STATUS_CHOICES = (
        (1, 'Draft'),
        (2, 'Submitted'),
        (3, 'In Review'),
        (4, 'Approved'),
        (5, 'Rejected'),
        (6, 'Removed'),
    )

    id = models.AutoField(primary_key=True)
    admin_remark = models.CharField(max_length=500, null=True, blank=True)
    title = models.CharField(max_length=100, null=False, blank=False)
    display_picture = models.CharField(max_length=500, null=False, blank=False)
    number_of_pages = models.IntegerField(default=0)
    description = models.CharField(max_length=500, null=False, blank=False)
    university_name = models.CharField(max_length=200, null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    course_code = models.CharField(max_length=100, null=True, blank=True)
    professor = models.CharField(max_length=100, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    selling_price = models.IntegerField(default=0)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    notes_preview = models.CharField(max_length=500, null=False, blank=False)
    file_name = models.CharField(max_length=100, null=False, blank=False)
    file = models.CharField(max_length=500, null=False, blank=False)
    file_size = models.IntegerField(default=0)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name='country_notes', null=True, blank=True)
    note_type = models.ForeignKey(NoteType, on_delete=models.DO_NOTHING, related_name='note_notes', null=True, blank=True)
    category = models.ForeignKey(NoteCategory, on_delete=models.DO_NOTHING, related_name='category_notes')
    seller = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='seller_notes')
    actioned_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='actioned_notes')
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_notes')
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='modified_notes')
    published_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

class Downloads(models.Model):
    id = models.AutoField(primary_key=True)
    is_seller_has_allowed_to_download = models.BooleanField(default=False)
    is_attachment_downloaded = models.BooleanField(default=False)
    attachment_downloaded_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    note = models.ForeignKey(SellerNotes, on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_downloads')
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='modified_downloads')
    seller = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='seller_downloads')
    downloader = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='downloader_downloads')

    def __str__(self):
        return f"{self.note.title}"

class SellerNotesReviews(models.Model):
    id = models.AutoField(primary_key=True)
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=500, null=False, blank=False)
    note = models.ForeignKey(SellerNotes, on_delete=models.DO_NOTHING)
    reviewed_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='reviewed_reviews')
    against_downloads = models.ForeignKey(Downloads, on_delete=models.DO_NOTHING, related_name='against_downloads_reviews')
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_reviews')
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='modified_reviews')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.rating}"


class SellerNotesReportedIssues(models.Model):
    id = models.AutoField(primary_key=True)
    remarks = models.CharField(max_length=500, null=False, blank=False)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_issues')
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='modified_issues')
    note = models.ForeignKey(SellerNotes, on_delete=models.DO_NOTHING)
    reported_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='reported_issues')
    against_downloads = models.ForeignKey(Downloads, on_delete=models.DO_NOTHING, related_name='against_downloads_issues')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.note.title}"