from PIL import Image, ImageFilter, ImageDraw, ImageFont
import random
import numpy as np

def draw(file_name, P, N, M=3):
    img = Image.open('images/'+file_name, 'r')
    pixels = img.load()
    size_x, size_y = img.size

    def dist(c1, c2):
        return (c1[0]-c2[0])**2+(c1[1]-c2[1])**2+(c1[2]-c2[2])**2

    def mean(colours):
        n = len(colours)
        return (
            sum(c[0] for c in colours)//n,
            sum(c[1] for c in colours)//n,
            sum(c[2] for c in colours)//n
        )

    def colourize(colour, palette):
        return min(palette, key=lambda c: dist(c, colour))

    def cluster(colours, k, max_n=10000, max_i=10):
        colours = random.sample(colours, max_n)
        centroids = random.sample(colours, k)
        i = 0; old = None
        while not(i>max_i or centroids==old):
            old = centroids; i+=1
            labels = [colourize(c, centroids) for c in colours]
            centroids = [mean([c for c,l in zip(colours, labels) if l==cen]) for cen in centroids]
        return centroids

    def label_map(palette):
        unique = list(set(palette))
        return {unique[i]:i for i in range(len(unique))}

    all_coords = [(x,y) for x in range(size_x) for y in range(size_y)]
    all_colours = [pixels[x,y] for x,y in all_coords]
    palette = cluster(all_colours, P)
    labels = label_map(palette)

    # kleurvastzetten
    for x,y in all_coords:
        pixels[x,y] = colourize(pixels[x,y], palette)
    img = img.filter(ImageFilter.MedianFilter(size=M))
    pixels = img.load()
    for x,y in all_coords:
        pixels[x,y] = colourize(pixels[x,y], palette)

    # segmentatie en mergelogica (vangt alle regio's samen)
    def neighbours(edge, outer, colour=None):
        return set(
            (x+a, y+b)
            for x,y in edge
            for a,b in ((1,0),(-1,0),(0,1),(0,-1))
            if (x+a,y+b) in outer and (colour is None or pixels[(x+a,y+b)]==colour)
        )

    def cell(centre, rest):
        colour = pixels[centre]; edge = {centre}; region=set()
        while edge:
            region |= edge
            rest -= edge
            edge = {n for n in neighbours(edge, rest, colour)}
        return region, rest

    rest = set(all_coords); cells=[]
    while rest:
        centre = random.sample(rest,1)[0]
        region, rest = cell(centre, rest-{centre})
        cells.append(region)
    cells.sort(key=len, reverse=True)

    # samenvoegen tot N regio's
    while len(cells)>N:
        small = cells.pop()
        nbs = neighbours(small, set(all_coords)-small)
        for big in cells:
            if big & nbs:
                big |= small
                break

    # paint regio's met gemiddelde kleur
    for cell in cells:
        colour = colourize(mean([pixels[x,y] for x,y in cell]), palette)
        for x,y in cell:
            pixels[x,y] = colour

    # omtrek en tekst (volledige implementatie overnemen uit de GitHub-repo)
    try:
        fnt = ImageFont.truetype("arial.ttf", 8)
    except:
        fnt = ImageFont.load_default()
    im_border = Image.new('RGB', img.size, (255,255,255))
    draw_obj = ImageDraw.Draw(im_border)
    # Hier moet de originele outline-logica uit de repo komen:
    # TODO: kopieer outline(), border(), tekstlocaties, etc. van de GitHub-bron

    im_border.save(f'images/P{P} N{N} OUTLINE{file_name}')
    img.save(f'images/P{P} N{N} {file_name}')
