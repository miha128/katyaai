// ==UserScript==
// @name         KatyaAI Watermark
// @namespace    http://tampermonkey.net/
// @version      Mal0
// @description  Katya Internal UserScript. Not for public use
// @author       Zenia Diamond
// @match        *://*/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    const imageUrl = "https://cdn.discordapp.com/attachments/1380955428074291353/1387148146596904970/SPOILER_KatyaCollab.png?ex=685c49e2&is=685af862&hm=4009042d8c15a2fb449d629dcdd3dd16020cdc3d53ab81bd86bfd8da41194bfa&";
    const imageSize = 20;
    const margin = 1;
    const floatingImg = document.createElement('img');
    floatingImg.src = imageUrl;
    floatingImg.style.position = 'fixed';
    floatingImg.style.bottom = margin + 'em';
    floatingImg.style.right = margin + 'em';
    floatingImg.style.width = imageSize + 'em';
    floatingImg.style.height = 'auto';
    floatingImg.style.opacity = '0.85';
    floatingImg.style.zIndex = '9999';
    floatingImg.style.pointerEvents = 'none';
    document.body.appendChild(floatingImg);
})();