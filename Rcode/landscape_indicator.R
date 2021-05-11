# simple landscape features indicator for Africa wildlife/nature tourism potential
# Based on absence/presence of landscape features: lakes, mountain peaks/ranges, coral reefs

library(tidyverse)
library(sf)
af <- st_read("./temp/af_countries_eez_islands.gpkg", layer = "af_countries_eez_islands")

# load lakes and mountain 
countries_gmba_glwd <- read_csv("../temp/countries_gmba_glwd.csv") %>%
  replace_na(list(gmba = 0, glwd_1 = 0)) %>%
  mutate(glwd = glwd_1 > 0) %>%
  mutate(gmbaT = gmba > 0) %>%
  select(-gmba) %>%
  rename(gmba = gmbaT) %>%
  select(iso3, gmba, glwd)
# load coral
countries_coral <- read_csv("../../../Marine/Af/coral_Af.csv") %>%
  mutate(coral = AreaSqkm > 5)%>%
  select(iso3, coral)
# join tables
# build combined indicator
af_landscape <- af %>%
  left_join(countries_gmba_glwd)%>%
  left_join(countries_coral) %>%
  replace_na(list(gmba = FALSE, coral = FALSE, glwd = FALSE)) %>%
  mutate(compensatory = gmba + coral + glwd) %>%
  mutate(non_compensatory = gmba | coral | glwd) %>%
  mutate(join = paste(
    if_else(glwd, "lakes", ""), 
    if_else(glwd & compensatory >1, " & ", ""),
    if_else(gmba, "moutains", ""),
    if_else(gmba & coral, " & ", ""),
    if_else(coral, "coral reefs", ""),
    sep = "")) %>%
  select(-path)
# export to gpkg
st_write(af_landscape, "../temp/af_landscape.gpkg", layer_options = "OVERWRITE=YES")
# export to csv (no geom)
file.remove("../temp/af_landscape.csv")
st_write(af_landscape, "../temp/af_landscape.csv")

theme_set(theme_bw())
p <- ggplot(af_landscape) +
  geom_sf(aes(fill = gmba)) +
  # scale_fill_ordinal() +
  labs(title="Presence of mountain range")
ggsave(filename = "../temp/gmba.png", plot = p)

p <- ggplot(af_landscape) +
  geom_sf(aes(fill = glwd)) +
  # scale_fill_ordinal() +
  labs(title="Presence of large lake/reservoir")
ggsave(filename = "../temp/glwd.png", plot = p)

p <- ggplot(af_landscape) +
  geom_sf(aes(fill = coral)) +
  # scale_fill_ordinal() +
  labs(title="Presence of warm water coral reefs")
ggsave(filename = "../temp/coral.png", plot = p)

p <- ggplot(af_landscape) +
  geom_sf(aes(fill = factor(compensatory))) +
  # scale_fill_ordinal() +
  labs(title="Presence of landscape features supporting nature tourism")
ggsave(filename = "../temp/compensatory.png", plot = p)

p <- ggplot(af_landscape) +
  geom_sf(aes(fill = non_compensatory)) +
  # scale_fill_ordinal() +
  labs(title="Presence of landscape features supporting nature tourism")
ggsave(filename = "../temp/non_compensatory.png", plot = p)

p <- ggplot(af_landscape) +
  geom_sf(aes(fill = join)) +
  # scale_fill_ordinal() +
  labs(title="Presence of landscape features supporting nature tourism")
ggsave(filename = "../temp/join.png", plot = p)
