from app import create_app, db
from app.models import Text, Word, Morph

app = create_app()

# для команды flask shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Text': Text, 'Word': Word, 'Morph': Morph}
