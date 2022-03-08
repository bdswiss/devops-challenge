import express = require("express");
import basicAuth = require("express-basic-auth");
const app = express();
const port = process.env.PORT;

app.get("/health", (_, res) => {
  res.send("Ok");
});

if (process.env.USERNAME && process.env.PASSWORD) {
  app.use(
    basicAuth({
      users: { [process.env.USERNAME]: process.env.PASSWORD }
    })
  );
}

app.get("/", (_, res) => {
  if (process.env.USERNAME) {
    res.send(`I work, and I am secure`);
  } else {
    res.send(`I work, but I am not secured`);
  }
});

app.listen(port, () => {
  console.log(`Challenge app listening on port ${port}`);
});
