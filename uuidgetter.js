//USE NODE V18 OR HIGHER

//node *thisfilename*.js -u *USERNAME*

const { argv } = require("node:process");

let user = argv.filter((arg) => {
  return argv.indexOf(arg) == argv.indexOf("-u") + 1;
});

const getuuid = async (resolve, reject) => {
  try {
    uuid = await fetch(`https://playerdb.co/api/player/minecraft/${user}`);
    uuid = await uuid.json();
    resolve(uuid.data.player.id);
  } catch (err) {
    console.log(err);
    reject(err);
  }
};

uuid = new Promise((resolve, reject) => {
  getuuid(resolve, reject);
}).then((uuid) => {
  console.log(uuid);
});
