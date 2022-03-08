# BDSwiss DevOps coding challenge
You're presented with a typical web application which consists of a web server and a worker.
To run the app you will need NodeJS 14+. Then you need to run `npm install` and finally build the app with `npm run build`.

Once you build the app the `dist/` folder will contain the transpiled server and worker that you can start with `node dist/server` and `node dist/worker`.

The application relies on the following env variables:

* PORT (server only) defines on which port to run
* INTERVAL a dummy variable defining the worker interval (Optional)
* USERNAME and PASSWORD secret to authenticated the user. (Optional)

Your objective if to package the application in a Docker container and prepare the deployment to AWS ECS using Cloud Development Kit. You're free to you any language that CDK supports that you feel most comfortable with.

The CDK code should be added to the application itself and create a task definition and ECS service for both web and the worker. The web service should scle based on the metric of your choice while worker should be a singleton and there should not be more than one wokrer running at any point in time.

Bonus: Read the INTERVAL variable from the SSM param store and the USERNAME/PASSWORD from the secrets manager.

Please submit your solution as a pull request to this repo.
