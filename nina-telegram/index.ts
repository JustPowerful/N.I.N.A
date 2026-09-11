import { Bot, Context, type CommandContext } from "grammy";
import { api } from "./lib/api-client";

const token = process.env.TELEGRAM_BOT_TOKEN;
const userId = process.env.TELEGRAM_USER_ID;
let requireUserId = false;

const userSessions = new Map<string, string>();

if (userId) {
  requireUserId = true;
}

if (!token) {
  throw new Error(
    "TELEGRAM_BOT_TOKEN is not defined in the environment variables.",
  );
}

async function keepTyping(ctx: Context) {
  const interval = setInterval(async () => {
    try {
      await ctx.api.sendChatAction(ctx.chat!.id, "typing");
    } catch (error) {
      console.error("Failed to send typing action:", error);
    }
  }, 4000);

  return () => clearInterval(interval);
}

const bot = new Bot(token);

function checkUserAuthorization(ctx: Context) {
  if (requireUserId && ctx.from?.id.toString() !== userId) {
    ctx.reply("You are not authorized to use this bot.");
    return false;
  }
  return true;
}

bot.command("start", async (ctx) => {
  // If there's a user ID set in the environment variables, check if the user is authorized
  if (!checkUserAuthorization(ctx)) {
    ctx.reply("You are not authorized to use this bot.");
    return;
  }

  // create a new session by calling the API
  try {
    const { data } = await api.post("/session/create", {
      title: `Telegram Session - ${new Date().toISOString()}`,
    });
    const sessionId = data.session_id;
    userSessions.set(ctx.from?.id.toString() || "", sessionId);
    await ctx.reply(
      `New session created with ID: ${sessionId}. You can now send messages to this bot, and they will be processed by the N.I.N.A AI Agent.`,
    );
  } catch (error) {
    console.error("Error creating session:", error);
    await ctx.reply("Failed to create a new session. Please try again later.");
  }
});

bot.on("message:text", async (ctx) => {
  try {
    // If there's a user ID set in the environment variables, check if the user is authorized
    if (!checkUserAuthorization(ctx)) {
      ctx.reply("You are not authorized to use this bot.");
      return;
    }

    // set the isTyping action to show the user that the bot is processing their message
    const stopTyping = await keepTyping(ctx);

    const userId = ctx.from?.id.toString() || "";
    const sessionId = userSessions.get(userId);

    if (!sessionId) {
      await ctx.reply(
        "No active session found. Please start a new session by sending /start.",
      );
      return;
    }

    const { data } = await api.post("/chat/send", {
      session_id: sessionId,
      message: ctx.message.text,
      generated_audio: false,
    });

    const chatResponse = data.response;

    // stop the typing action before sending the response
    stopTyping();

    await ctx.reply(chatResponse);
  } catch (error) {
    console.error("Error processing message:", error);
    await ctx.reply("Failed to process your message. Please try again later.");
  }
});

await bot.start();
