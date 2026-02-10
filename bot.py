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
LOG_PATH = Path("data/orders.log")


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

CATEGORY_THUMBNAILS = {
    "Sea event": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTCElE9E66MeeIElmqlQrfPgr25y7ByYpcFQg&s",
    "Farm": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxot0PY6NZvtQihOMjwfIbHJGk3hFUq4-C0w&s",
    "Item": "data:image/jpeg;base64,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",
    "Race": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQL01frRpa5-pPaNofH8XGcmXtXzxHSCrRv1g&s",
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


def write_order_log(entry: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(entry + "\n")


def ensure_order_counter(state: dict) -> None:
    if "order_counter" not in state:
        state["order_counter"] = 1


def get_next_order_id(state: dict) -> int:
    ensure_order_counter(state)
    order_id = state["order_counter"]
    state["order_counter"] = order_id + 1
    return order_id


def add_history_entry(user_id: int, category: str, product: Product, status: str) -> None:
    state = load_state()
    history = state.setdefault("history", {})
    user_history = history.setdefault(str(user_id), [])
    user_history.insert(
        0,
        {
            "category": category,
            "label": product.label,
            "price": product.price,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
    )
    history[str(user_id)] = user_history[:20]
    save_state(state)

def add_order_entry(user_id: int, category: str, product: Product) -> dict:
    state = load_state()
    order_id = get_next_order_id(state)
    order = {
        "order_id": order_id,
        "user_id": user_id,
        "category": category,
        "label": product.label,
        "price": product.price,
        "status": "Chờ xử lý",
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    orders = state.setdefault("orders", [])
    orders.insert(0, order)
    state["orders"] = orders[:200]
    save_state(state)
    write_order_log(
        f"[{order['timestamp']}] order_id={order_id} user_id={user_id} "
        f"category={category} label={product.label} price={product.price} status=Chờ xử lý"
    )
    return order


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
            value=(
                f"**Danh mục:** {item['category']}\n"
                f"**Giá:** {item['price']}\n"
                f"**Trạng thái:** {item.get('status', 'Chờ xử lý')}\n"
                f"**Thời gian:** {item['timestamp']}"
            ),
            inline=False,
        )
    return embed


def build_home_embed() -> discord.Embed:
    return discord.Embed(
        title="🏠 Trang chủ",
        description=(
            "Chào mừng bạn đến với shop!\n"
            "Chọn mục bên dưới để xem dịch vụ, quản trị, hoặc lịch sử mua hàng.\n\n"
            "⚠️ **Rủi ro:** Dịch vụ phụ thuộc vào tình trạng game/ server. "
            "Shop không chịu trách nhiệm khi có sự cố ngoài ý muốn."
        ),
        color=discord.Color.from_rgb(88, 101, 242),
    )


def build_category_embed(category: str) -> discord.Embed:
    products = PRODUCTS.get(category, [])
    lines = [f"• **{item.label}** — {item.price}" for item in products]
    description = "\n".join(lines) if lines else "Chưa có sản phẩm."
    embed = discord.Embed(
        title=f"⚔️ Cày thuê - {category}",
        description=description,
        color=discord.Color.green(),
    )
    thumbnail = CATEGORY_THUMBNAILS.get(category)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    return embed


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
        order = add_order_entry(interaction.user.id, self.category, product)
        add_history_entry(
            interaction.user.id, self.category, product, order["status"]
        )
        embed = build_product_detail_embed(self.category, product)
        embed.add_field(name="Mã đơn", value=str(order["order_id"]), inline=True)
        embed.add_field(name="Trạng thái", value=order["status"], inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await send_order_log(interaction, order)


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

async def send_order_log(interaction: discord.Interaction, order: dict) -> None:
    log_channel_id = os.getenv("LOG_CHANNEL_ID")
    if not log_channel_id:
        return
    channel = interaction.client.get_channel(int(log_channel_id))
    if channel is None:
        return
    embed = discord.Embed(
        title="🧾 Log đơn hàng mới",
        color=discord.Color.teal(),
    )
    embed.add_field(name="Mã đơn", value=str(order["order_id"]), inline=True)
    embed.add_field(name="Trạng thái", value=order["status"], inline=True)
    embed.add_field(name="Danh mục", value=order["category"], inline=True)
    embed.add_field(name="Dịch vụ", value=order["label"], inline=True)
    embed.add_field(name="Giá", value=order["price"], inline=True)
    embed.add_field(name="User ID", value=str(order["user_id"]), inline=True)
    embed.set_footer(text=order["timestamp"])
    await channel.send(embed=embed)

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


@bot.tree.command(name="cap-nhat-don", description="Cập nhật trạng thái đơn hàng")
@app_commands.checks.has_permissions(administrator=True)
async def cap_nhat_don(
    interaction: discord.Interaction, order_id: int, status: str
) -> None:
    state = load_state()
    orders = state.get("orders", [])
    target = next((item for item in orders if item["order_id"] == order_id), None)
    if not target:
        await interaction.response.send_message(
            "Không tìm thấy đơn hàng.", ephemeral=True
        )
        return
    target["status"] = status
    save_state(state)
    write_order_log(
        f"[{datetime.utcnow().isoformat(timespec='seconds')}Z] "
        f"order_id={order_id} status_updated={status} by_admin={interaction.user.id}"
    )
    await interaction.response.send_message(
        f"Đã cập nhật trạng thái đơn {order_id} thành **{status}**.",
        ephemeral=True,
    )

def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN chưa được cấu hình.")
    bot.run(token)


if __name__ == "__main__":
    main()
