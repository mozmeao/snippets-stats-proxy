@Library('github.com/mozmar/jenkins-pipeline@20170315.1')
def config
def deployProd = false

conduit {
  node {
    stage("Prepare") {
      checkout scm
      setGitEnvironmentVariables()

      try {
        config = readYaml file: "jenkins.yml"
      }
      catch (e) {
        config = []
      }
      println "config ==> ${config}"

      if (!config || (config && config.pipeline && config.pipeline.enabled == false)) {
        println "Pipeline disabled."
      }
    }

    docker_image = "${config.project.docker_name}:${GIT_COMMIT_SHORT}"

    stage("Build") {
      if (!dockerImageExists(docker_image)) {
        sh "echo 'ENV GIT_SHA ${GIT_COMMIT}' >> Dockerfile"
        dockerImageBuild(docker_image, ["pull": true])
      }
      else {
        echo "Image ${docker_image} already exists."
      }
    }

    stage("Upload Images") {
      dockerImagePush(docker_image, "mozjenkins-docker-hub")
    }
  }

  milestone()

  node {
    onTag(/\d{4}\d{2}\d{2}.\d{1,2}/) {
      deployProd = true
    }
  }

  if (deployProd) {
    for (deploy in config.deploy.prod) {
      stage ("Deploying to ${deploy.name}") {
        timeout(time: 10, unit: 'MINUTES') {
          input("Push to ${deploy.name}?")
        }
        node {
          lock("push to ${deploy.name}") {
            deis_executable = deploy.deis_executable ?: "deis"
            deisLogin(deploy.url, deploy.credentials, deis_executable) {
              deisPull(deploy.app, docker_image, null, deis_executable)
            }
          }
        }
      }
    }
  }
}
