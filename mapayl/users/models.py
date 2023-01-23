from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import uuid


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError(_('The given email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Default user for P2P Lending."""

    #: First and last name do not cover name patterns around the globe
    objects = UserManager()

    name = CharField(_("Name of User"), blank=True, max_length=255)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    KYC_STATUS = (
        ('unverified', _('Unverified')),
        ('verified', _('Verified')),
        ('pending', _('Pending')),
        ('action_required', _('Action Required')),
        ('cancelled', _('Cancelled')),
        ('failed', _('Failed')),
        ('rejected', _('Rejected')),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("""The unique identifier of the instance this object belongs to.
                    Mandatory, unless a new instance to create is given."""))

    first_name = models.CharField(
        verbose_name=_('First names'),
        max_length=125,
        blank=True, null=True,
        help_text=_("Legal First names of the client."))

    last_name = models.CharField(
        verbose_name=_('Last names'),
        max_length=125,
        blank=True, null=True,
        help_text=_("Legal Last names of the client."))

    email = models.CharField(
        verbose_name=_('Email Address'),
        max_length=125,
        unique=True,
        help_text=_("Email address of the client."))

    current_address = models.CharField(
        verbose_name=_('current address'),
        max_length=1000,
        blank=True, null=True,
        help_text=_("The current living address of the borrower. Verification is required"))

    permanent_address = models.CharField(
        verbose_name=_('permanent address'),
        max_length=1000,
        blank=True, null=True,
        help_text=_("Permanent living address of the borrower. Verification and privacy rules applies"))

    contact_number = models.CharField(
        verbose_name=_('contact number'),
        max_length=20,
        blank=True, null=True,
        help_text=_("International format of borrower's contact number. Phone number if provided must be unique"))

    date_of_birth = models.DateField(
        verbose_name=_('date of birth'),
        blank=True, null=True,
        help_text=_("Date of birth of borrower. Registered borrowers must be not less than 18 years of age "))

    kyc_complete = models.BooleanField(
        verbose_name=_('kyc_complete'),
        default=False,
        help_text=_("Indication if borrower has completing KYC verification processes"))

    kyc_complete_date = models.DateTimeField(
        verbose_name=_('date of kyc completion'),
        blank=True, null=True,
        help_text=_("KYC complete date"))

    kyc_status = models.CharField(
        verbose_name=_('kyc status'),
        choices=KYC_STATUS,
        default="unverified",
        max_length=20,
        help_text=_("kyc status of the client."))

    on_boarding_complete = models.BooleanField(
        verbose_name=_('on boarding status'),
        default=False,
        help_text=_("on boarding status of the client."))

    on_boarding_complete_date = models.DateTimeField(
        verbose_name=_('date of on_boarding completion'),
        blank=True, null=True,
        help_text=_("on boarding complete date"))

    kyc_submitted = models.BooleanField(
        verbose_name=_('kyc submitted'),
        default=False,
        help_text=_("Indication if borrower has submitted KYC verification processes"))

    aadhar_number = models.CharField(
        verbose_name=_('aadhar number'),
        max_length=20,
        blank=True, null=True,
        help_text=_("AAdhar number. Must be unique"))

    place_of_birth = models.CharField(
        verbose_name=_('place of birth'),
        max_length=125,
        blank=True, null=True,
        help_text=_("The birth place of borrower"))

    verification_date = models.DateTimeField(
        verbose_name=_('verification date'),
        default=timezone.now,
        blank=True, null=True,
        help_text=_("The verification date of borrower"))

    registered_ip_address = models.CharField(
        verbose_name=_('registered ip address'),
        max_length=125,
        blank=True, null=True,
        help_text=_("The registered ip address of client"))

    country_of_residence = models.CharField(
        verbose_name=_('country of residence'),
        max_length=125,
        blank=True, null=True,
        help_text=_("The country of residence of borrower"))

    job_title = models.CharField(
        verbose_name=_('job title'),
        max_length=125,
        blank=True, null=True,
        help_text=_("The job title of borrower"))
    default_currency = models.CharField(
        verbose_name=_('default currency'),
        max_length=3,
        default='INR',
        blank=True, null=True,
        help_text=_("The default currency of borrower"))

    ################################################################
    ################ pending models ################################
    ################################################################

    # pending_cash_balance
    # time_zone
    # salutation
    # highest_qualification
    # passout_year
    # investment_limit
    # fund_committed
    # escrow_account_number
    # tax_id

    class Meta:
        verbose_name = _("Registered User")
        verbose_name_plural = _("Registered Users")

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.id})
