# Parrot's Sticky Bot

Hark! Could it be? A sticky bot *you* can host??

## What is it?

This is a sticky bot I wrote a while ago that I am making the code publicly available.
Right now, the bot does the following things:

- Makes sticky messages that stay at the bottom of a channel. Very good for describing rules for channels,
  or prompting people.
- Easily remove sticky messages with one simple command!
- On start up, refreshes sticky messages that got buried during the shutdown.

## How to use it?

For hosting, you can use any service that supports Python and PostgreSQL.
I personally use Railway which is cheap for most projects, but anything works. (Even your own PC!)

### Setting up the Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
2. Name it whatever you want, then click the `Bot` tab on the left.
3. If you want a new icon, you can upload one here. Down in the Privileged Gateway Intents section, make sure to enable
   the `Message Content Intent`. Then click `Save Changes`.
4. Copy the token of your bot, which you will need later to host the bot.
5. Go to the `OAuth2` tab, then the `URL Generator` subtab. Under scopes, select `bot`. Then under bot permissions,
   select `Manage Messages`, `Read Message History`, and `Send Messages`. Copy the generated URL and open it in a new
   tab to invite the bot to your server.

Bang, discord bot is made. Now to make it work!

### Hosting with Railway

1. Create a new project on Railway.
2. Create a new PostgreSQL database in the project, and copy the `DATABASE_URL` found in the `Variables` tab for later.
3. In the `Database` tab of the PostgreSQL DB, paste the contents of [the schema](https://github.com/OccultParrot/ParrotStickyBot/blob/main/schema.sql) into the SQL command box.
4. Create a new project on Railway, and paste this repository's URL when prompted to connect a GitHub repository.
   ![Your Railway should look like this after step 4](https://github.com/OccultParrot/ParrotStickyBot/blob/main/assets/railway.png)

Your Railway should look like the image above after step 3

5. In the `Variables` tab of the ParrotStickyBot node, add the following variables:
    * `DATABASE_URL`: The `DATABASE_URL` you copied from the PostgreSQL database you created in step 2.
    * `GUILD_ID`: The id of the server you want to deploy to. You can keep this empty if you want to deploy to multiple
      servers.
    * `OWNER_ID`: Your Discord user id. This is used to give you access to all the commands, regardless of your roles.
    * `TOKEN`: The token of the bot you created on the Discord Developer Portal.

   :warning: ***NEVER SHARE THE CONTENTS OF ANY OF THESE VARIABLES*** :warning:

   ![Your Variables Should Look Like this](https://github.com/OccultParrot/ParrotStickyBot/blob/main/assets/variables.png?raw=true)

Your Variables should look like the image above after step 5

6. Click the `Deploy` button and wait for it to finish. Once it's done, the bot should be online in your server!

## License
This project is under a MIT license. Please refer to the LICENSE file for more information.
