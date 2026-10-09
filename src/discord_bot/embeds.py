import discord 

def build_beatmapset_embed(data: dict) -> discord.Embed:
    beatmapset_id = data["id"]

    embed = discord.Embed(
        description=(
            f"**{data.get('artist')} - "
            f"{data.get('title')}**\n\n"
            f"[Maplink](https://osu.ppy.sh/beatmapsets/{beatmapset_id})\n"
            f"Mapper: [{data.get('creator')}]"
            f"(https://osu.ppy.sh/users/{data.get('user_id')})\n"
            f"Status: {data.get('status')}"
        ),
        color=discord.Colour.from_rgb(255, 102, 171)
    )

    embed.set_image(
        url=f"https://assets.ppy.sh/beatmaps/{beatmapset_id}/covers/cover.jpg"
    )

    beatmaps = [
        beatmap for beatmap in data.get("beatmaps", [])
        if beatmap.get("mode") == "osu"
    ]
    
    beatmaps = sorted(
        beatmaps,
        key=lambda beatmap: beatmap.get("difficulty_rating"),
        reverse=True
    )
    
    for beatmap in beatmaps[:5]:
        version = beatmap.get("version")
        stars = beatmap.get("difficulty_rating")

        ar = beatmap.get("ar", 0)
        od = beatmap.get("accuracy", 0)
        hp = beatmap.get("drain", 0)
        cs = beatmap.get("cs", 0)

        total_seconds = beatmap.get("total_length")
        minutes, seconds = divmod(total_seconds, 60)
        length = f"{minutes}:{seconds:02d}"

        max_combo = beatmap.get("max_combo")

        embed.add_field(
            name=f"⭐ {version} - {stars:.2f}★",
            value=(
                f"**AR:** {ar} ▸ **OD:** {od} ▸ "
                f"**HP:** {hp} ▸ **CS:** {cs}\n"
                f"**Length:** {length} ▸ **Max Combo:** {max_combo}x"
            ),
            inline=False
        )

        embed.set_footer(text=f"Beatmapset ID: {beatmapset_id}")

    
    return embed