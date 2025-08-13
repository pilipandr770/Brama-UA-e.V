from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    remember = BooleanField(_l('Запам\'ятати мене'))
    submit = SubmitField(_l('Увійти'))

class RegistrationForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Пароль'), validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(_l('Повторіть пароль'), validators=[
        DataRequired(), 
        EqualTo('password', message=_l('Паролі повинні співпадати.'))
    ])
    first_name = StringField(_l('Ім\'я'), validators=[DataRequired()])
    last_name = StringField(_l('Прізвище'), validators=[DataRequired()])
    birth_date = DateField(_l('Дата народження'), format='%Y-%m-%d', validators=[Optional()])
    specialty = StringField(_l('Спеціалізація'), validators=[Optional()])
    join_goal = TextAreaField(_l('Мета участі'), validators=[Optional()])
    can_help = TextAreaField(_l('Чим можете допомогти'), validators=[Optional()])
    want_to_do = TextAreaField(_l('Чим бажаєте займатися'), validators=[Optional()])
    phone = StringField(_l('Телефон'), validators=[Optional()])
    consent_given = BooleanField(_l('Даю згоду на обробку персональних даних'), validators=[DataRequired()])
    submit = SubmitField(_l('Зареєструватися'))

class EditProfileForm(FlaskForm):
    first_name = StringField(_l('Ім\'я'), validators=[DataRequired()])
    last_name = StringField(_l('Прізвище'), validators=[DataRequired()])
    birth_date = DateField(_l('Дата народження'), format='%Y-%m-%d', validators=[Optional()])
    specialty = StringField(_l('Спеціалізація'), validators=[Optional(), Length(max=128)])
    join_goal = TextAreaField(_l('Мета участі'), validators=[Optional(), Length(max=256)])
    can_help = TextAreaField(_l('Чим можете допомогти'), validators=[Optional(), Length(max=256)])
    want_to_do = TextAreaField(_l('Чим бажаєте займатися'), validators=[Optional(), Length(max=256)])
    phone = StringField(_l('Телефон'), validators=[Optional(), Length(max=32)])
    profile_photo = FileField(_l('Фото профілю'), validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], _l('Тільки файли формату JPG, JPEG або PNG!'))
    ])
    submit = SubmitField(_l('Зберегти зміни'))
