# This script should be called from within Hudson

VENV=$WORKSPACE/venv

echo "Starting build..."

if [ ! -d "$VENV/bin" ]; then
  echo "No virtualenv found.  Making one..."
  virtualenv --no-site-packages $VENV
fi

source $VENV/bin/activate

pip install -q -r requirements.txt

cat > local_settings.py <<SETTINGS
from settings import *
ROOT_URLCONF = 'workspace.urls'
SETTINGS

echo "Starting tests..."
python manage.py test --noinput --with-coverage --with-xunit --with-xcoverage --cover-package=workspace

echo "Building documentation..."
cd docs
make dirhtml

echo 'shazam!'