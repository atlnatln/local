/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Level Data (32 statik seviye)
   ═══════════════════════════════════════════════════════════ */

export const LEVELS_BY_AGE = {

  '5-6': [
    { title: 'İlk Adım', desc: 'Sayıyı sağa taşı!', cols: 3, rows: 1, startX: 0, startY: 0, startVal: 1, targetX: 2, targetY: 0, targetVal: null, walls: [], ops: [], commands: ['x+'], maxCmds: 4, stars: [2, 3] },
    { title: 'Aşağı İn', desc: 'Sayıyı aşağı götür!', cols: 1, rows: 3, startX: 0, startY: 0, startVal: 2, targetX: 0, targetY: 2, targetVal: null, walls: [], ops: [], commands: ['y+'], maxCmds: 4, stars: [2, 3] },
    { title: 'Köşeye Git', desc: 'Sağ alta ulaş!', cols: 3, rows: 3, startX: 0, startY: 0, startVal: 3, targetX: 2, targetY: 2, targetVal: null, walls: [], ops: [], commands: ['x+', 'y+'], maxCmds: 6, stars: [4, 5] },
    { title: 'Geri Dön', desc: 'Sol tarafa git!', cols: 3, rows: 1, startX: 2, startY: 0, startVal: 5, targetX: 0, targetY: 0, targetVal: null, walls: [], ops: [], commands: ['x-'], maxCmds: 4, stars: [2, 3] },
    { title: 'Yukarı Çık', desc: 'Yukarıya git!', cols: 1, rows: 3, startX: 0, startY: 2, startVal: 4, targetX: 0, targetY: 0, targetVal: null, walls: [], ops: [], commands: ['y-'], maxCmds: 4, stars: [2, 3] },
    { title: 'L Yolu', desc: 'L şeklinde ilerle!', cols: 3, rows: 3, startX: 0, startY: 0, startVal: 6, targetX: 2, targetY: 2, targetVal: null, walls: [[1,0],[2,0],[2,1]], ops: [], commands: ['x+', 'y+'], maxCmds: 6, stars: [4, 5] },
    { title: 'Zigzag', desc: 'Duvarlardan kaç!', cols: 4, rows: 3, startX: 0, startY: 0, startVal: 7, targetX: 3, targetY: 2, targetVal: null, walls: [[1,0],[2,1]], ops: [], commands: ['x+', 'x-', 'y+', 'y-'], maxCmds: 8, stars: [5, 7] },
    { title: 'Kestirme', desc: 'En kısa yoldan git!', cols: 4, rows: 4, startX: 0, startY: 0, startVal: 8, targetX: 3, targetY: 3, targetVal: null, walls: [[1,1],[2,2]], ops: [], commands: ['x+', 'y+', 'x-', 'y-'], maxCmds: 10, stars: [6, 8] },
  ],

  '7-8': [
    { title: 'Sayı Taşı', desc: 'Sayıyı hedefe götür!', cols: 3, rows: 3, startX: 0, startY: 0, startVal: 3, targetX: 2, targetY: 2, targetVal: null, walls: [], ops: [], commands: ['x+', 'y+'], maxCmds: 6, stars: [4, 5] },
    { title: 'Duvar Aşma', desc: 'Duvarın etrafından dolaş!', cols: 4, rows: 3, startX: 0, startY: 0, startVal: 5, targetX: 3, targetY: 0, targetVal: null, walls: [[2,0],[2,1]], ops: [], commands: ['x+', 'x-', 'y+', 'y-'], maxCmds: 8, stars: [6, 7] },
    { title: 'Değer Değiştir', desc: 'Sayını 5 yap ve hedefe götür!', cols: 3, rows: 1, startX: 0, startY: 0, startVal: 3, targetX: 2, targetY: 0, targetVal: 5, walls: [], ops: [], commands: ['x+', 'z+', 'z-'], maxCmds: 6, stars: [4, 5] },
    { title: 'Toplama Yolu', desc: 'Sayıyı büyüt ve hedefe ulaş!', cols: 4, rows: 1, startX: 0, startY: 0, startVal: 1, targetX: 3, targetY: 0, targetVal: 4, walls: [], ops: [], commands: ['x+', 'z+'], maxCmds: 8, stars: [6, 7] },
    { title: 'Çıkarma Yolu', desc: 'Sayıyı küçült!', cols: 3, rows: 1, startX: 0, startY: 0, startVal: 8, targetX: 2, targetY: 0, targetVal: 5, walls: [], ops: [], commands: ['x+', 'z-'], maxCmds: 6, stars: [5, 6] },
    { title: 'Toplama Hücreleri', desc: 'Özel hücreler sayını değiştirir!', cols: 4, rows: 3, startX: 0, startY: 0, startVal: 2, targetX: 3, targetY: 2, targetVal: 5, walls: [[1,1]], ops: [{x:2,y:0,type:'+',val:1},{x:3,y:1,type:'+',val:2}], commands: ['x+', 'y+', 'y-'], maxCmds: 8, stars: [5, 7] },
    { title: 'Labirent', desc: 'Duvarların arasından geç!', cols: 5, rows: 4, startX: 0, startY: 0, startVal: 7, targetX: 4, targetY: 3, targetVal: null, walls: [[1,0],[1,1],[3,2],[3,3],[2,2]], ops: [], commands: ['x+', 'x-', 'y+', 'y-'], maxCmds: 12, stars: [7, 10] },
    { title: 'Karma Bulmaca', desc: 'Hem taşı hem değiştir!', cols: 4, rows: 4, startX: 0, startY: 0, startVal: 2, targetX: 3, targetY: 3, targetVal: 6, walls: [[1,1],[2,2]], ops: [{x:1,y:0,type:'+',val:2}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 12, stars: [8, 10] },
    { title: 'Büyük Macera', desc: 'Her şeyi kullan!', cols: 5, rows: 5, startX: 0, startY: 0, startVal: 1, targetX: 4, targetY: 4, targetVal: 10, walls: [[2,0],[0,2],[3,3]], ops: [{x:1,y:1,type:'+',val:3},{x:3,y:2,type:'+',val:2}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 16, stars: [10, 14] },
  ],

  '9-10': [
    { title: 'Çarpma Kapısı', desc: 'x2 hücresinden geçerek hedefe ulaş!', cols: 5, rows: 3, startX: 0, startY: 1, startVal: 3, targetX: 4, targetY: 1, targetVal: 6, walls: [[2,0],[2,2]], ops: [{x:2,y:1,type:'×',val:2}], commands: ['x+', 'x-', 'y+', 'y-'], maxCmds: 8, stars: [4, 6] },
    { title: 'Sayı Fabrikası', desc: 'Doğru değerle bitir!', cols: 5, rows: 5, startX: 0, startY: 0, startVal: 1, targetX: 4, targetY: 4, targetVal: 12, walls: [[1,1],[3,1],[1,3],[3,3]], ops: [{x:2,y:0,type:'+',val:2},{x:4,y:2,type:'×',val:2},{x:2,y:4,type:'+',val:3}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 14, stars: [8, 12] },
    { title: 'Çift Duvar', desc: 'Labirentin derinliklerine in!', cols: 6, rows: 5, startX: 0, startY: 0, startVal: 5, targetX: 5, targetY: 4, targetVal: null, walls: [[1,0],[1,1],[1,2],[3,2],[3,3],[3,4],[5,0],[5,1]], ops: [], commands: ['x+', 'x-', 'y+', 'y-'], maxCmds: 15, stars: [9, 13] },
    { title: 'Hesap Makinesi', desc: 'Topla, çık, ilerle!', cols: 5, rows: 4, startX: 0, startY: 3, startVal: 2, targetX: 4, targetY: 0, targetVal: 10, walls: [[2,1],[3,2]], ops: [{x:1,y:3,type:'+',val:3},{x:3,y:0,type:'×',val:2}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 14, stars: [8, 12] },
    { title: 'Karar Noktası', desc: 'Hangi yoldan gideceksin?', cols: 5, rows: 5, startX: 2, startY: 0, startVal: 4, targetX: 2, targetY: 4, targetVal: 8, walls: [[0,1],[4,1],[1,2],[3,2],[0,3],[4,3]], ops: [{x:2,y:1,type:'+',val:1},{x:2,y:3,type:'×',val:2}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 12, stars: [6, 10] },
    { title: 'Spiral', desc: 'Spiral yoldan geç!', cols: 5, rows: 5, startX: 0, startY: 0, startVal: 1, targetX: 2, targetY: 2, targetVal: null, walls: [[1,0],[1,1],[1,2],[1,3],[3,1],[3,2],[3,3],[3,4],[2,4],[0,2]], ops: [], commands: ['x+', 'x-', 'y+', 'y-'], maxCmds: 16, stars: [12, 14] },
    { title: 'Değer Avcısı', desc: 'Tam değerle bitir!', cols: 6, rows: 4, startX: 0, startY: 0, startVal: 1, targetX: 5, targetY: 3, targetVal: 15, walls: [[2,0],[4,1],[1,2],[3,3]], ops: [{x:1,y:0,type:'×',val:3},{x:5,y:1,type:'+',val:5},{x:3,y:2,type:'×',val:2}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 18, stars: [10, 15] },
    { title: 'Usta Seviye', desc: 'Tüm becerilerin gerekli!', cols: 6, rows: 6, startX: 0, startY: 0, startVal: 2, targetX: 5, targetY: 5, targetVal: 20, walls: [[1,0],[3,0],[4,0],[1,2],[2,2],[4,2],[4,3],[0,4],[1,4],[3,4]], ops: [{x:2,y:0,type:'+',val:3},{x:5,y:2,type:'×',val:2},{x:2,y:4,type:'+',val:5}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 20, stars: [12, 17] },
  ],

  '11-12': [
    { title: 'Mühendis Köprüsü', desc: 'Karmaşık yoldan geç!', cols: 7, rows: 5, startX: 0, startY: 0, startVal: 3, targetX: 6, targetY: 4, targetVal: null, walls: [[1,0],[1,1],[3,1],[3,2],[3,3],[5,2],[5,3],[5,4]], ops: [], commands: ['x+', 'x-', 'y+', 'y-'], maxCmds: 16, stars: [11, 14] },
    { title: 'Formül Oluştur', desc: 'Sayını tam 24 yap!', cols: 6, rows: 5, startX: 0, startY: 2, startVal: 2, targetX: 5, targetY: 2, targetVal: 24, walls: [[1,1],[2,0],[4,3],[4,4]], ops: [{x:1,y:2,type:'×',val:3},{x:3,y:2,type:'×',val:2},{x:5,y:0,type:'+',val:5}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 14, stars: [7, 11] },
    { title: 'Çoklu İşlem', desc: 'Her adım önemli!', cols: 7, rows: 5, startX: 0, startY: 0, startVal: 1, targetX: 6, targetY: 4, targetVal: 30, walls: [[2,0],[2,1],[4,2],[4,3],[6,0],[6,1]], ops: [{x:1,y:0,type:'×',val:2},{x:3,y:1,type:'+',val:4},{x:5,y:3,type:'×',val:3}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 18, stars: [10, 15] },
    { title: 'Mega Labirent', desc: 'Büyük labirentten çık!', cols: 7, rows: 7, startX: 0, startY: 0, startVal: 5, targetX: 6, targetY: 6, targetVal: null, walls: [[1,0],[1,1],[3,0],[5,0],[5,1],[5,2],[1,3],[2,3],[3,3],[3,4],[1,5],[1,6],[3,6],[5,4],[5,5]], ops: [], commands: ['x+', 'x-', 'y+', 'y-'], maxCmds: 24, stars: [12, 20] },
    { title: 'Denklem Yolu', desc: 'Sayıyı 50 yap!', cols: 7, rows: 6, startX: 0, startY: 0, startVal: 2, targetX: 6, targetY: 5, targetVal: 50, walls: [[2,1],[4,0],[4,1],[0,3],[1,3],[5,3],[6,3],[2,4]], ops: [{x:1,y:0,type:'×',val:5},{x:3,y:2,type:'+',val:10},{x:6,y:2,type:'×',val:2}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 20, stars: [10, 16] },
    { title: 'Strateji Oyunu', desc: 'Doğru rota çok önemli!', cols: 7, rows: 7, startX: 3, startY: 0, startVal: 1, targetX: 3, targetY: 6, targetVal: 36, walls: [[1,1],[5,1],[0,3],[2,3],[4,3],[6,3],[1,5],[5,5]], ops: [{x:3,y:1,type:'×',val:3},{x:1,y:3,type:'+',val:6},{x:5,y:3,type:'×',val:2},{x:3,y:5,type:'+',val:3}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 20, stars: [10, 16] },
    { title: 'Hacker Challenge', desc: 'En az komutla bitir!', cols: 8, rows: 6, startX: 0, startY: 0, startVal: 1, targetX: 7, targetY: 5, targetVal: 100, walls: [[2,0],[2,1],[4,1],[4,2],[6,2],[6,3],[0,3],[0,4],[2,4],[2,5]], ops: [{x:1,y:0,type:'×',val:5},{x:3,y:2,type:'×',val:2},{x:5,y:3,type:'+',val:10},{x:7,y:4,type:'×',val:2}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 24, stars: [12, 20] },
    { title: 'Büyük Final', desc: 'Tüm bilgilerini kullan!', cols: 8, rows: 8, startX: 0, startY: 0, startVal: 1, targetX: 7, targetY: 7, targetVal: 64, walls: [[1,0],[1,1],[3,0],[5,1],[5,2],[7,0],[7,1],[0,3],[2,3],[2,4],[4,3],[4,4],[6,4],[6,5],[0,6],[1,6],[3,6],[3,7],[5,6]], ops: [{x:2,y:0,type:'×',val:2},{x:6,y:2,type:'×',val:2},{x:1,y:4,type:'×',val:2},{x:5,y:5,type:'×',val:2},{x:2,y:7,type:'×',val:2}], commands: ['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], maxCmds: 28, stars: [14, 22] },
  ],
};
