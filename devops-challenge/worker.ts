console.log("Starting the worker");

setInterval(() => {
  console.log("I am alive", new Date().toISOString());
}, Number(process.env.INTERVAL || 1000));
