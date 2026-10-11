<?xml version="1.0" encoding="UTF-8"?>
<!--
  Browser view for feeds/AIMarketMaps.xml.
  Feed readers ignore this file; it only changes what people see when they
  open the feed in a browser that serves it as XML (e.g. via GitHub Pages).
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>

  <xsl:variable name="feedUrl">https://raw.githubusercontent.com/joylarkin/Awesome-AI-Market-Maps/main/feeds/AIMarketMaps.xml</xsl:variable>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title><xsl:value-of select="/rss/channel/title"/></title>
        <style>
          :root {
            --bg: #ffffff; --fg: #1f2328; --muted: #59636e; --line: #d1d9e0;
            --accent: #0969da; --box: #f6f8fa;
          }
          @media (prefers-color-scheme: dark) {
            :root {
              --bg: #0d1117; --fg: #e6edf3; --muted: #9198a1; --line: #3d444d;
              --accent: #4493f8; --box: #151b23;
            }
          }
          * { box-sizing: border-box; }
          body {
            margin: 0; background: var(--bg); color: var(--fg);
            font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
          }
          main { max-width: 820px; margin: 0 auto; padding: 32px 16px 64px; }
          h1 { font-size: 1.6rem; line-height: 1.25; margin: 0 0 8px; }
          a { color: var(--accent); text-decoration: none; }
          a:hover { text-decoration: underline; }
          .desc { color: var(--muted); margin: 0 0 20px; }
          .subscribe {
            background: var(--box); border: 1px solid var(--line); border-radius: 8px;
            padding: 14px 16px; margin: 0 0 28px; font-size: 0.95rem;
          }
          .subscribe code {
            display: block; margin-top: 8px; padding: 8px 10px; overflow-x: auto;
            background: var(--bg); border: 1px solid var(--line); border-radius: 6px;
            font: 0.85rem ui-monospace, SFMono-Regular, Menlo, monospace; white-space: nowrap;
          }
          .count { color: var(--muted); font-size: 0.9rem; margin: 0 0 8px; }
          ul { list-style: none; margin: 0; padding: 0; }
          li { padding: 12px 0; border-top: 1px solid var(--line); }
          li a { font-weight: 600; overflow-wrap: anywhere; }
          .meta { color: var(--muted); font-size: 0.85rem; margin-top: 2px; }
          .tag {
            display: inline-block; margin-right: 8px; padding: 0 8px; border-radius: 999px;
            border: 1px solid var(--line); font-size: 0.8rem;
          }
        </style>
      </head>
      <body>
        <main>
          <h1>
            <a href="{/rss/channel/link}">Awesome AI Market Maps</a> RSS Feed
          </h1>
          <p class="desc"><xsl:value-of select="/rss/channel/description"/></p>

          <div class="subscribe">
            <strong>This is an RSS feed.</strong>
            Copy this URL into your feed reader or workflow to subscribe:
            <code><xsl:value-of select="$feedUrl"/></code>
          </div>

          <p class="count"><xsl:value-of select="count(/rss/channel/item)"/> market maps</p>
          <ul>
            <xsl:for-each select="/rss/channel/item">
              <li>
                <a href="{link}"><xsl:value-of select="title"/></a>
                <div class="meta">
                  <xsl:if test="category">
                    <span class="tag"><xsl:value-of select="category"/></span>
                  </xsl:if>
                  <xsl:value-of select="substring(pubDate, 6, 11)"/>
                </div>
              </li>
            </xsl:for-each>
          </ul>
        </main>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
