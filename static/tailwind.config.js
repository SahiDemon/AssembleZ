module.exports = {
  "theme": {
    "extend": {
      "colors": {
        "Success": {
          "300": "#199033",
          "500": "#32A94C",
          "700": "#4CC366"
        },
        "Danger": {
          "300": "#A22020",
          "500": "#BF2626",
          "700": "#E14747"
        },
        "Gray": {
          "500": "#595959",
          "700": "#999999",
          "900": "#D9D9D9",
          "Black": "#000000",
          "White": "#FFFFFF"
        },
        "Primary": {
          "100": "#003EB3",
          "300": "#0074F0",
          "500": "#14A9FF",
          "700": "#85DCFF"
        },
        "foreground": "#000000",
        "background": "#FFFFFF"
      },
      "spacing": {
        "OneAndHalfUnits": "24px",
        "FiveUnits": "80px",
        "HalfUnit": "8px",
        "TwoUnits": "32px",
        "SixUnits": "96px",
        "FourUnits": "64px",
        "ThreeUnits": "48px",
        "Unit": "16px"
      },
      "borderRadius": {
        "Radius2": "2px",
        "Radius8": "8px",
        "Round": "50%",
        "Radius4": "4px"
      },
      "scale": {
        "XSmall": "16px",
        "XLarge": "192px",
        "XXLarge": "288px",
        "MaxWidth": "1400px",
        "Small": "48px",
        "Large": "144px",
        "Medium": "96px"
      }
    }
  },
  "plugins": [],
  "content": [
    "./src/**/*.{html,js,ts,jsx,tsx}",
    "./*.html"
  ]
}