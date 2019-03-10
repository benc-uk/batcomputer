# Postman Collection

This is an exported Postman collection with a series of API test calls, in order to test the Batcomputer model API. Each call also has test cases defined

This collection can be used to run integration tests during the release pipeline using the Newman tool, and the JUnit reporter

This snippet assumes you have two input artifacts, one named `batcomputer-src` for the Git repo, and one called `acr-image` for the image pushed to ACR. The variable `API_HOST` should also be set

```
steps:
- bash: 'npm install -g newman --prefix $(System.DefaultWorkingDirectory) '
  displayName: 'Install Newman'

- bash: |
   cd batcomputer-src
   $(System.DefaultWorkingDirectory)/bin/newman run ./tests/Batcomputer.postman_collection.json -r junit --timeout 60000 --reporter-junit-export test-results.xml --global-var api-host="$(API_HOST)"
  displayName: 'Run Tests'

- task: PublishTestResults@2
  displayName: 'Publish Test Results'
  inputs:
    testResultsFiles: 'test-results.xml'
    searchFolder: '$(System.DefaultWorkingDirectory)/batcomputer-src/'
```

You can also import this into Postman client, the collection uses just one variable `api-host` which should be set to the API hostname and port, e.g. `localhost:8000`
