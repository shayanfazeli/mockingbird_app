from flask import Blueprint, render_template
import os
from app import cache_folderpath
from app.libraries.io.read_write import write_pkl_gz, read_pkl_gz
from app.blueprints.email_notification.forms import EmailNotificationForm

email_notification_blueprint = Blueprint("email_notification", __name__)


@email_notification_blueprint.route('/email_notification/<request_type>/<request_id>', methods=['GET', 'POST'])
def email_notification(request_type: str, request_id: str):
    assert request_type in ['word_cloud', 'word_frequency', 'topic_modeling']

    form = EmailNotificationForm()
    if form.validate_on_submit():
        args = dict()
        args['email'] = form.email.data

        if args['email'] is not None and args['email'] != '':
            if os.path.exists(os.path.join(cache_folderpath, 'requests/emails', f'{request_type}_{request_id}.pkl.gz')):
                emails = read_pkl_gz(os.path.join(cache_folderpath, 'requests/emails', f'{request_type}_{request_id}.pkl.gz'))
            else:
                emails = []
            emails = set(emails)
            emails.add(args['email'])
            write_pkl_gz(list(emails), os.path.join(cache_folderpath, 'requests/emails', f'{request_type}_{request_id}.pkl.gz'))
            return render_template("email_notification/success.html", email_provided=True)
        return render_template("email_notification/success.html", email_provided=False)
    return render_template("email_notification/form.html", form=form)
