# Ninja Game 🥷

2D platformová akční hra vytvořená v Pygame s důrazem na rychlý pohyb, přesné skákání a eliminaci nepřátel.

## 📖 Popis

Ninja Game je pixel-art platformovka, kde hráč ovládá ninja bojovníka procházejícího náročnými úrovněmi plnými nepřátel a parkuru. Hra kombinuje plynulý pohyb, dash mechaniky a střelbu projektilů s postupně se zvyšující obtížností.

## ✨ Klíčové funkce

### Herní mechaniky
- **Pohybový systém** – běh, skok, dvojitý skok, wall slide a dash
- **Bojový systém** – střelba projektilů nepřátele
- **Dash mechanika** – rychlý úhyb s invulnerabilitou
- **Fyzikální engine** – realistická gravitace, kolize se stěnami a podlahou
- **AI nepřátelé** – autonomní nepřátelé s vlastním chováním a střelbou

### Herní režimy a obtížnost
- **3 úrovně obtížnosti:**
  - BABY MODE – lehký režim pro začátečníky
  - NORMAL – standardní výzva
  - HARD – hardcore režim pro zkušené hráče
- **Systém levelů** – postupně se zvyšující obtížnost
- **Tracking statistik** – sledování času a pokusů

### UI a menu systém
- **Hlavní menu** s leaderboardy pro každou obtížnost
- **Nastavení** – přepínání SFX a výběr obtížnosti
- **Pauza menu** – možnost pokračovat, zobrazit nastavení nebo opustit hru
- **End screen** – zobrazení výsledků a možnost uložení do leaderboardu

### Vizuální efekty
- **Pixel-art grafika** s autentickým retro stylem
- **Animace** – plynulé animace pro všechny akce hráče i nepřátel
- **Částicové efekty** – listy padající ze stromů, jiskry z projektilů
- **Screen shake** – dynamický efekt otřesů při zásazích
- **Clouds system** – animované mraky na pozadí
- **Scrollování kamery** – sledování hráče s plynulým pohybem

### Audio
- **Zvukové efekty:**
  - Skok
  - Dash
  - Zásah
  - Střelba
  - Ambientní zvuky
- **Hudba na pozadí** – atmosférická hudba na smyčce
- **Možnost vypnutí SFX** v nastavení

### Editor úrovní
- **Vestavěný level editor** (`editor.py`)
- Umožňuje vytváření vlastních map
- Podpora různých typů dlaždic (grass, stone, decor, spawners)
- Ukládání a načítání map ve formátu JSON

### Technické funkce
- **Tilemap systém** – efektivní správa herní mapy
- **Respawn systém** – návrat na začátek úrovně při smrti
- **Leaderboard** – ukládání a načítání nejlepších výsledků
- **Resizable okno** – možnost měnit velikost herního okna
- **60 FPS** – plynulý běh hry

## 🎮 Ovládání

### V menu
- **W/S nebo ↑/↓** – navigace v menu
- **Enter/Mezerník** – potvrzení výběru
- **ESC** – návrat/ukončení

### Ve hře
- **A/D nebo ←/→** – pohyb doleva/doprava
- **W nebo mezerník** – skok (dvojitý skok od zdi)
- **SHIFT** – dash (rychlý úhyb)
- **ESC** – pauza

### V editoru
- **WASD nebo šipky** – pohyb kamery
- **SHIFT** – přepínání režimu
- **Levé tlačítko myši** – umístění dlaždice
- **Pravé tlačítko myši** – odstranění dlaždice
- **O** – uložení mapy

## 🏗️ Technologie

- **Python 3**
- **Pygame** – herní framework
- **JSON** – formát pro ukládání map a dat

## 📂 Struktura projektu

```
Ninja_game/
├── data/
│   ├── images/        # Grafické assety
│   ├── maps/          # JSON soubory s úrovněmi
│   ├── sfx/           # Zvukové efekty
│   └── music. wav      # Hudba na pozadí
├── scripts/
│   ├── entities. py    # Herní entity (hráč, nepřátelé)
│   ├── tilemap.py     # Správa mapy
│   ├── clouds.py      # Systém mraků
│   ├── particle.py    # Částicové efekty
│   ├── spark.py       # Jiskřící efekty
│   ├── UI.py          # Uživatelské rozhraní
│   ├── menu.py        # Systém menu
│   ├── leaderboard.py # Žebříček
│   └── utils.py       # Pomocné funkce
├── game.py            # Hlavní herní smyčka
└── editor.py          # Level editor
```

## 🚀 Spuštění hry

```bash
python Ninja_game/game.py
```

## 🔧 Spuštění editoru

```bash
python Ninja_game/editor.py
```

## 🎯 Herní cíle

- Projít všemi úrovněmi co nejrychleji
- Minimalizovat počet úmrtí
- Porazit všechny nepřátele
- Dosáhnout nejlepšího času v leaderboardu
- Zvládnout hru na HARD obtížnosti

## 📊 Leaderboard systém

Hra automaticky ukládá nejlepší výsledky pro každou obtížnost.

---

**Vytvořeno jako semestrální projekt 2025**

## 3. Finální stav projektu

- Projekt je rozdělen na dvě části: **Corebound** a **Ninja Game**
- **Ninja Game** má hotovou herní smyčku (*game loop*) a slouží jako technický základ pro Corebound
- **Corebound** je nedokončená verze, která však obsahuje téměř všechny původní plánované cíle, funkce a To-Do prvky minulého readme.
