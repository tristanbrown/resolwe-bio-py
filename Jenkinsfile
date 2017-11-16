node {
    def workspace_dir = pwd()
    // Genialis Base branch with which to run the End-to-End tests
    def genialis_base_e2e_tests_branch = "master"
    // directory where to check out the given branch of Genialis Base
    def genialis_base_dir = "genialis-base"
    // NOTE: To avoid exceeding the maximum allowed shebang lenght when calling pip due very
    // long paths of Jenkins' workspaces, we need to set a shorter Tox's working directory path
    // More info: http://tox.readthedocs.io/en/latest/example/jenkins.html#avoiding-the-path-too-long-error-with-long-shebang-lines
    def tox_workdir = "${env.HOME}/.tox-${env.BUILD_TAG}"
    // extra arguments passed to Tox
    def tox_extra_args = ""
    if (genialis_base_e2e_tests_branch == "master") {
        // NOTE: If we are running End-to-End tests with Genialis Base's "master" branch, we
        // need to allow installing pre-releases with the pip command.
        tox_extra_args += "--pre"
    }
    // path of the JUnit report
    def junit_report_file = "${genialis_base_dir}/.reports/resdk_e2e_report.xml"

    try {
        stage("Checkout") {
            // check out the same revision as this script is loaded from
            checkout scm
        }

        stage("Prepare (E2E)") {
            // remove JUnit report from the previous run (if it exists)
            if (fileExists(junit_report_file)) {
                sh "rm ${junit_report_file}"
            }

            // check if we trust the author who has submitted this change or if a branch from the
            // main repository is being built
            // NOTE: This is necessary since we don't want to expose Genialis Base code base to
            // unauthorized people.
            // NOTE: This is a work-around until the GitHub Branch Source Plugin authors implement
            // a way to configure which pull requests from forked repositories are trusted and
            // which not. More info at:
            // https://github.com/jenkinsci/github-branch-source-plugin/pull/96
            // https://issues.jenkins-ci.org/browse/JENKINS-36240
            def change_author = env.CHANGE_AUTHOR
            def trusted_authors = [
                "dblenkus",
                "kostko",
                "JenkoB",
                "jkokosar",
                "JureZmrzlikar",
                "mstajdohar",
                "tjanez",
                "jvrakor",
                "mzganec"
            ]
            if (change_author != null && ! trusted_authors.contains(change_author)) {
                // NOTE: The change_author variable equals null if a branch from the main
                // repository is being built
                error "User '${change_author}' is not yet trusted to build pull requests. \
                    Please, contact maintainers!"
            }

            // check out the given branch of Genialis Base
            dir(genialis_base_dir) {
                git (
                    [url: "https://github.com/genialis/genialis-base.git",
                     branch: "${genialis_base_e2e_tests_branch}",
                     credentialsId: "c89baeb1-9818-4627-95fd-50eeb3677a39",
                     changelog: false,
                     poll: false]
                )
            }

            // create an empty configuration schema to avoid an error about it not being available
            // when calling manage.py
            dir(genialis_base_dir) {
                sh "mkdir -p frontend/genjs/schema && \
                    echo '{}' > frontend/genjs/schema/configuration.json"
            }
        }

        stage("Test (E2E)") {
            // run End-to-End tests
            dir(genialis_base_dir) {
                withEnv(["GENESIS_POSTGRESQL_USER=postgres",
                         "GENESIS_POSTGRESQL_PORT=55440",
                         // set database name to a unique value
                         "GENESIS_POSTGRESQL_NAME=${env.BUILD_TAG}",
                         "GENESIS_ES_PORT=59210",
                         // NOTE: Genialis Base's Django settings automatically set the
                         // ELASTICSEARCH_INDEX_PREFIX to 'test_' if the 'manage.py test' command
                         // is run. Additionally, 'resolwe.elastic' app's logic also automatically
                         // appends a random ID to test index prefixes to avoid index name clashes.
                         "GENESIS_REDIS_PORT=56390",
                         // Processes need to be registered for e2e tests, but don't need to be
                         // run, so there is no need to pull Docker images.
                         "GENESIS_DOCKER_DONT_PULL=1",
                         "GENESIS_RESDK_PATH=${workspace_dir}",
                         "TOX_WORKDIR=${tox_workdir}"]) {
                    lock (resource: "resolwe-bio-py-e2e-lock-redis10-liveserver8090") {
                        withEnv(["GENESIS_REDIS_DATABASE=10",
                                 "GENESIS_TEST_LIVESERVER_PORT=8090"]) {
                            // NOTE: End-to-End tests could hang unexpectedly and lock the
                            // "resolwe-bio-py-e2e-lock" indefinitely thus we have to set a timeout
                            // on their execution time.
                            timeout(time: 15, unit: "MINUTES") {
                                sh "tox -e py34-e2e-resdk ${tox_extra_args}"
                            }
                        }
                    }
                }
            }
            if (! fileExists(junit_report_file)) {
                error "JUnit report not found at '${junit_report_file}'."
            }
        }

    } catch (e) {
        currentBuild.result = "FAILED"
        // report failures only when testing the "master" branch
        if (env.BRANCH_NAME == "master") {
            notifyFailed()
        }
        throw e
    } finally {
        // record JUnit report
        if (fileExists(junit_report_file)) {
            junit junit_report_file
        }
        // manually remove Tox's working directory since it is created outside Jenkins's
        // workspace
        sh "rm -rf ${tox_workdir}"
    }
}

def notifyFailed() {
    slackSend(
        color: "#FF0000",
        message: "FAILED: Job ${env.JOB_NAME} (build #${env.BUILD_NUMBER}) ${env.BUILD_URL}"
    )
}
