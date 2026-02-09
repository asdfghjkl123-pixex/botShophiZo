import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import discord
from discord import app_commands
from discord.ext import commands

STATE_PATH = Path("data/state.json")


@dataclass(frozen=True)
class Product:
    label: str
    description: str
    price: str


PRODUCTS: Dict[str, List[Product]] = {
    "Sea event": [
        Product("Săn boss biển", "Đi theo team săn boss", "150,000đ"),
        Product("Bảo vệ tàu", "Hộ tống tàu an toàn", "100,000đ"),
    ],
    "Farm": [
        Product("Farm level", "Cày cấp nhanh", "200,000đ"),
        Product("Farm tài nguyên", "Thu thập vật phẩm", "120,000đ"),
    ],
    "Item": [
        Product("Item hiếm", "Săn item theo yêu cầu", "300,000đ"),
        Product("Craft item", "Chế tạo vật phẩm", "180,000đ"),
    ],
    "Race": [
        Product("Đua top", "Boost thứ hạng", "250,000đ"),
        Product("Giải đấu", "Hỗ trợ thi đấu", "220,000đ"),
    ],
}


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)


def add_history_entry(user_id: int, category: str, product: Product) -> None:
    state = load_state()
    history = state.setdefault("history", {})
    user_history = history.setdefault(str(user_id), [])
    user_history.insert(
        0,
        {
            "category": category,
            "label": product.label,
            "price": product.price,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
    )
    history[str(user_id)] = user_history[:20]
    save_state(state)


def build_history_embed(user_id: int) -> discord.Embed:
    state = load_state()
    entries = state.get("history", {}).get(str(user_id), [])
    embed = discord.Embed(
        title="📜 Lịch sử dịch vụ",
        description="Danh sách dịch vụ bạn đã xem/chọn gần đây.",
        color=discord.Color.blurple(),
    )
    if not entries:
        embed.add_field(
            name="Chưa có lịch sử",
            value="Hãy chọn dịch vụ ở mục **Cày Thuê** để lưu vào lịch sử.",
            inline=False,
        )
        return embed

    for item in entries[:10]:
        embed.add_field(
            name=f"🧾 {item['label']}",
            value=f"**Danh mục:** {item['category']}\n**Giá:** {item['price']}\n**Thời gian:** {item['timestamp']}",
            inline=False,
        )
    return embed


def build_home_embed() -> discord.Embed:
    return discord.Embed(
        title="🏠 Trang chủ",
        description=(
            "Chào mừng bạn đến với shop!\n"
            "Chọn mục bên dưới để xem dịch vụ, quản trị, hoặc lịch sử mua hàng."
        ),
        color=discord.Color.from_rgb(88, 101, 242),
    )


def build_category_embed(category: str) -> discord.Embed:
    products = PRODUCTS.get(category, [])
    lines = [f"• **{item.label}** — {item.price}" for item in products]
    description = "\n".join(lines) if lines else "Chưa có sản phẩm."
    return discord.Embed(
        title=f"⚔️ Cày thuê - {category}",
        description=description,
        color=discord.Color.green(),
    )


def build_product_detail_embed(category: str, product: Product) -> discord.Embed:
    return discord.Embed(
        title=product.label,
        description=product.description,
        color=discord.Color.gold(),
    ).add_field(name="Danh mục", value=category, inline=True).add_field(
        name="Giá", value=product.price, inline=True
    )


class ProductSelect(discord.ui.Select):
    def __init__(self, category: str):
        self.category = category
        options = [
            discord.SelectOption(
                label=item.label,
                description=item.price,
                value=item.label,
            )
            for item in PRODUCTS.get(category, [])
        ]
        super().__init__(
            placeholder="Chọn sản phẩm",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"product_select:{category}",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        selected = self.values[0]
        product = next(
            (item for item in PRODUCTS.get(self.category, []) if item.label == selected),
            None,
        )
        if not product:
            await interaction.response.send_message(
                "Sản phẩm không tồn tại.", ephemeral=True
            )
            return
        add_history_entry(interaction.user.id, self.category, product)
        embed = build_product_detail_embed(self.category, product)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ProductSelectView(discord.ui.View):
    def __init__(self, category: str):
        super().__init__(timeout=300)
        if PRODUCTS.get(category):
            self.add_item(ProductSelect(category))


class CayThueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="Sea event", style=discord.ButtonStyle.primary, custom_id="cay:sea")
    async def sea_event(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await send_category(interaction, "Sea event")

    @discord.ui.button(label="Farm", style=discord.ButtonStyle.primary, custom_id="cay:farm")
    async def farm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await send_category(interaction, "Farm")

    @discord.ui.button(label="Item", style=discord.ButtonStyle.primary, custom_id="cay:item")
    async def item(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await send_category(interaction, "Item")

    @discord.ui.button(label="Race", style=discord.ButtonStyle.primary, custom_id="cay:race")
    async def race(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await send_category(interaction, "Race")


class HomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Cày Thuê",
        style=discord.ButtonStyle.success,
        custom_id="home:cay_thue",
    )
    async def cay_thue(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        embed = discord.Embed(
            title="🛒 Cày thuê",
            description="Chọn dịch vụ cày thuê bên dưới.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(
            embed=embed, view=CayThueView(), ephemeral=True
        )

    @discord.ui.button(
        label="Cài Đặt (quyền admin)",
        style=discord.ButtonStyle.secondary,
        custom_id="home:settings",
    )
    async def settings(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Bạn không có quyền admin để dùng mục này.", ephemeral=True
            )
            return
        embed = discord.Embed(
            title="⚙️ Cài đặt",
            description="Khu vực cài đặt dành cho admin.",
            color=discord.Color.orange(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Lịch Sử",
        style=discord.ButtonStyle.secondary,
        custom_id="home:history",
    )
    async def history(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        embed = build_history_embed(interaction.user.id)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def send_category(interaction: discord.Interaction, category: str) -> None:
    embed = build_category_embed(category)
    view = ProductSelectView(category)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ShopBot(commands.Bot):
    async def setup_hook(self) -> None:
        self.add_view(HomeView())
        self.add_view(CayThueView())


intents = discord.Intents.default()
intents.guilds = True
intents.message_content = False

bot = ShopBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    state = load_state()
    channel_id = os.getenv("HOME_CHANNEL_ID")
    if not channel_id:
        print("HOME_CHANNEL_ID chưa được cấu hình.")
        return
    channel = bot.get_channel(int(channel_id))
    if channel is None:
        print("Không tìm thấy kênh Trang chủ.")
        return

    message_id = state.get("home_message_id")
    if message_id:
        try:
            message = await channel.fetch_message(int(message_id))
            await message.edit(embed=build_home_embed(), view=HomeView())
            print("Đã cập nhật Trang chủ.")
            return
        except discord.NotFound:
            state.pop("home_message_id", None)
        except discord.DiscordException as exc:
            print(f"Không thể cập nhật Trang chủ: {exc}")
            return

    message = await channel.send(embed=build_home_embed(), view=HomeView())
    state["home_message_id"] = message.id
    save_state(state)
    print("Đã tạo Trang chủ.")


@bot.tree.command(name="tao-trang-chu", description="Tạo lại embed Trang chủ")
@app_commands.checks.has_permissions(administrator=True)
async def tao_trang_chu(interaction: discord.Interaction) -> None:
    embed = build_home_embed()
    view = HomeView()
    await interaction.response.send_message(embed=embed, view=view)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN chưa được cấu hình.")
    bot.run(token)


if __name__ == "__main__":
    main()
