pipeline {
    agent {
        label 'irrigation-python'
    }

    options {
        skipDefaultCheckout(true)
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                script {
                    env.CI_PYTHON = sh(
                        script: '''
                            for candidate in python3.11 python3; do
                                if command -v "$candidate" >/dev/null 2>&1; then
                                    printf '%s\\n' "$candidate"
                                    exit 0
                                fi
                            done
                            exit 1
                        ''',
                        returnStdout: true
                    ).trim()
                }
                sh '''
                    set -eu
                    "$CI_PYTHON" -c 'import sys; print("Python {}".format(sys.version.split()[0])); sys.version_info >= (3, 11) or sys.exit("Python 3.11+ is required")'
                    "$CI_PYTHON" -m venv .venv
                    .venv/bin/python -m pip install --disable-pip-version-check \
                        "pip==25.3" \
                        "setuptools==80.9.0" \
                        "ruff==0.14.4" \
                        "pytest==8.4.2"
                    .venv/bin/python -m pip install --disable-pip-version-check \
                        --no-build-isolation --no-deps -e .
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '.venv/bin/ruff check src tests'
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    set -eu
                    mkdir -p reports
                    .venv/bin/python -m pytest -q tests --junitxml=reports/pytest.xml
                '''
            }
        }

        stage('Publish test results') {
            steps {
                junit testResults: 'reports/pytest.xml', allowEmptyResults: false
            }
        }
    }

    post {
        always {
            script {
                if (currentBuild.currentResult != 'SUCCESS' && fileExists('reports/pytest.xml')) {
                    junit testResults: 'reports/pytest.xml', allowEmptyResults: false
                }
            }
            deleteDir()
        }
        success {
            echo 'SUCCESS'
        }
        failure {
            echo 'FAILURE'
        }
        aborted {
            echo 'FAILURE'
        }
    }
}