from sqlalchemy.orm import sessionmaker, scoped_session

from app import create_app, db
from app.models import Text, Word, Morph


app = create_app()

with app.app_context():
    engine = db.session.get_bind()
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

# для команды flask shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Text': Text, 'Word': Word, 'Morph': Morph,
            'Session': Session}
