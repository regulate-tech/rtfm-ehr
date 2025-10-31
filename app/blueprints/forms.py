# --- app/blueprints/forms.py ---
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp, NumberRange, ValidationError

class AddPmiForm(FlaskForm):
    """Form for adding a new patient to the PMI."""
    nhs_number = StringField('NHS Number', validators=[DataRequired(), Length(10, 10), Regexp('^[0-9]*$')])
    title = StringField('Title', validators=[Optional(), Length(max=35)])
    given_name = StringField('Given Name', validators=[DataRequired(), Length(max=100)])
    family_name = StringField('Family Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('', '-- Select --'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[Optional()])
    address_line_1 = StringField('Address Line 1', validators=[Optional(), Length(max=255)])
    address_line_2 = StringField('Address Line 2', validators=[Optional(), Length(max=255)])
    town_or_city = StringField('Town/City', validators=[Optional(), Length(max=100)])
    county = StringField('County', validators=[Optional(), Length(max=100)])
    postcode = StringField('Postcode', validators=[Optional(), Length(max=8)])
    phone_mobile = StringField('Mobile Phone', validators=[Optional(), Length(max=20)])
    phone_home = StringField('Home Phone', validators=[Optional(), Length(max=20)])
    email_address = StringField('Email Address', validators=[Optional(), Email(), Length(max=254)])
    submit = SubmitField('Add Patient')

class BatchPmiForm(FlaskForm):
    """Form for specifying the number of batch PMI records to create."""
    num_records = IntegerField('Number of Records', validators=[DataRequired(), NumberRange(min=1, max=500)])
    submit = SubmitField('Create Batch Records')

class SearchPmiForm(FlaskForm):
    """Form for searching PMI/EHR by NHS Number."""
    nhs_number = StringField('NHS Number', validators=[DataRequired(), Length(10, 10), Regexp('^[0-9]*$')])
    submit = SubmitField('Search / Create EHR') # Button text adjusted in admin template

class DataEntrySearchForm(FlaskForm):
    """Form for searching EHR by NHS Number for data entry."""
    nhs_number = StringField('NHS Number', validators=[DataRequired(), Length(10, 10), Regexp('^[0-9]*$')])
    submit = SubmitField('Find EHR')

class VitalSignsForm(FlaskForm):
    """Form for entering basic vital signs (BP)."""
    systolic = IntegerField('Systolic Pressure (mmHg)', validators=[DataRequired(), NumberRange(min=30, max=300)])
    diastolic = IntegerField('Diastolic Pressure (mmHg)', validators=[DataRequired(), NumberRange(min=20, max=200)])
    submit = SubmitField('Submit Vitals')

class PatientSearchForm(FlaskForm):
    """Form for patients to search for their records."""
    nhs_number = StringField('NHS Number (Optional)', validators=[Optional(), Length(10, 10), Regexp('^[0-9]*$')])
    given_name = StringField('Given Name (Optional)', validators=[Optional(), Length(max=100)])
    family_name = StringField('Family Name (Optional)', validators=[Optional(), Length(max=100)])
    date_of_birth = DateField('Date of Birth (Optional)', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Search My Records')

    def validate(self, extra_validators=None):
        initial_validation = super(PatientSearchForm, self).validate(extra_validators)
        if not initial_validation: return False
        has_nhs = bool(self.nhs_number.data)
        has_demographics = bool(self.given_name.data and self.family_name.data and self.date_of_birth.data)
        if not has_nhs and not has_demographics:
            msg = 'Provide NHS Number OR full name and date of birth.'
            self.nhs_number.errors.append(msg)
            self.given_name.errors.append('Required if no NHS Number.')
            self.family_name.errors.append('Required if no NHS Number.')
            self.date_of_birth.errors.append('Required if no NHS Number.')
            return False
        return True

class GeneralSearchForm(FlaskForm):
    """
    A simple form for a general search term.
    """
    term = StringField('Search Term', validators=[DataRequired()])
    submit = SubmitField('Search')

class DeletePmiForm(FlaskForm):
    """
    A simple form that just provides a 'submit' button
    for secure, token-protected deletion.
    """
    submit = SubmitField('Delete')

class CsrfOnlyForm(FlaskForm):
    """An empty form used purely for CSRF token generation."""
    pass
