@Library('github.com/mozmar/jenkins-pipeline@20170303.1')
def config

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
      node {
        stage ("Deploying to ${deploy.name}") {
          lock("push to ${deploy.name}") {
            deisLogin(deploy.url, deploy.credentials) {
              deisPull(deploy.app, docker_image)
            }
          }
        }
      }
    }
  }
}
