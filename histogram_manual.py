from PIL import Image
import matplotlib.pyplot as plt

# --- Histogram teks per‐channel ---
def tampilkan_histogram_teks_rgb(hists, judul):
    print(f"\n{judul}")
    print("Channel | Intensitas : Jumlah Piksel | Visualisasi")
    print("-" * 70)
    colors = {'R':'\033[31m', 'G':'\033[32m', 'B':'\033[34m'}  # ANSI merah/hijau/biru
    reset = '\033[0m'
    for ch, hist in hists.items():
        max_val = max(hist)
        print(f"{ch} channel:")
        for i in range(256):
            if hist[i] > 0:
                bar = '█' * int((hist[i] / max_val) * 40)
                print(f"  {str(i).rjust(3)} : {str(hist[i]).rjust(7)} | {colors[ch]}{bar}{reset}")
        print()

# --- Hitung histogram RGB ---
def hitung_histogram_rgb(img):
    w, h = img.size
    hists = {'R':[0]*256, 'G':[0]*256, 'B':[0]*256}
    for y in range(h):
        for x in range(w):
            r,g,b = img.getpixel((x,y))
            hists['R'][r] += 1
            hists['G'][g] += 1
            hists['B'][b] += 1
    return hists

# --- CDF per‐channel ---
def hitung_cdf(hist):
    cdf = [0]*256
    cdf[0] = hist[0]
    for i in range(1,256):
        cdf[i] = cdf[i-1] + hist[i]
    return cdf

# --- Equalization per channel ---
def equalize_rgb(img):
    w,h = img.size
    hists = hitung_histogram_rgb(img)
    cdfs = {ch: hitung_cdf(hists[ch]) for ch in hists}
    total = w*h
    eq_map = {}
    for ch in cdfs:
        cdf = cdfs[ch]
        cdf_min = min(val for val in cdf if val>0)
        eq_map[ch] = [ round((cdf[i]-cdf_min)/(total-cdf_min)*255) for i in range(256) ]

    out = Image.new('RGB', img.size)
    out_hists = {'R':[0]*256,'G':[0]*256,'B':[0]*256}
    for y in range(h):
        for x in range(w):
            r,g,b = img.getpixel((x,y))
            nr = eq_map['R'][r]
            ng = eq_map['G'][g]
            nb = eq_map['B'][b]
            out.putpixel((x,y), (nr,ng,nb))
            out_hists['R'][nr] += 1
            out_hists['G'][ng] += 1
            out_hists['B'][nb] += 1

    return out, out_hists

# --- Specification per channel (sumber→target) ---
def specify_rgb(src, tgt):
    w,h = src.size
    h_src = hitung_histogram_rgb(src)
    h_tgt = hitung_histogram_rgb(tgt)
    c_src = {ch: hitung_cdf(h_src[ch]) for ch in h_src}
    c_tgt = {ch: hitung_cdf(h_tgt[ch]) for ch in h_tgt}
    total_src = w*h
    total_tgt = tgt.size[0]*tgt.size[1]
    norm_src = {ch:[v/total_src for v in c_src[ch]] for ch in c_src}
    norm_tgt = {ch:[v/total_tgt for v in c_tgt[ch]] for ch in c_tgt}

    map_ch = {}
    for ch in norm_src:
        map_ch[ch] = []
        for i in range(256):
            tgt_idx = min(range(256), key=lambda j: abs(norm_src[ch][i] - norm_tgt[ch][j]))
            map_ch[ch].append(tgt_idx)

    out = Image.new('RGB', src.size)
    out_hists = {'R':[0]*256,'G':[0]*256,'B':[0]*256}
    for y in range(h):
        for x in range(w):
            r,g,b = src.getpixel((x,y))
            nr = map_ch['R'][r]
            ng = map_ch['G'][g]
            nb = map_ch['B'][b]
            out.putpixel((x,y),(nr,ng,nb))
            out_hists['R'][nr] += 1
            out_hists['G'][ng] += 1
            out_hists['B'][nb] += 1

    return out, out_hists

# --- Fungsi plot dengan matplotlib ---
def tampilkan_gambar_dan_histogram_rgb(img, hists, judul_gambar, judul_hist):
    plt.figure(figsize=(10,4))
    plt.subplot(1,2,1)
    plt.imshow(img)
    plt.title(judul_gambar)
    plt.axis('off')

    plt.subplot(1,2,2)
    xs = list(range(256))
    plt.bar(xs, hists['R'], color='r', alpha=0.6, label='R')
    plt.bar(xs, hists['G'], color='g', alpha=0.6, label='G')
    plt.bar(xs, hists['B'], color='b', alpha=0.6, label='B')
    plt.title(judul_hist)
    plt.xlabel('Intensitas')
    plt.ylabel('Jumlah Piksel')
    plt.legend()
    plt.tight_layout()
    plt.show()

# === MAIN ===
# 1) Buka gambar input dan gambar referensi (RGB)
input_img     = Image.open('inp.jpg').convert('RGB')
reference_img = Image.open('ref.jpeg').convert('RGB')

# 2) Hitung & tampilkan histogram input
h_input = hitung_histogram_rgb(input_img)
tampilkan_histogram_teks_rgb(h_input, "Histogram Input (RGB)")
tampilkan_gambar_dan_histogram_rgb(input_img, h_input,
    "Gambar Input (RGB)", "Histogram Input")

# 3) Equalization pada input
eq_img, h_eq = equalize_rgb(input_img)
tampilkan_histogram_teks_rgb(h_eq, "Histogram Setelah Equalization (RGB)")
eq_img.save("hasil_equalization_rgb.png")
tampilkan_gambar_dan_histogram_rgb(eq_img, h_eq,
    "Hasil Equalization RGB", "Histogram Equalization")

# 4) Specification: input → reference
sp_img, h_sp = specify_rgb(input_img, reference_img)
tampilkan_histogram_teks_rgb(h_sp, "Histogram Setelah Specification (RGB)")
sp_img.save("hasil_specification_rgb.png")
tampilkan_gambar_dan_histogram_rgb(sp_img, h_sp,
    "Hasil Specification RGB", "Histogram Specification")

print("Selesai — file disimpan:\n"
      " - hasil_equalization_rgb.png\n"
      " - hasil_specification_rgb.png")

