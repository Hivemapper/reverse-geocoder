import argparse, os
import pandas as pd
import googlemaps


# USAGE: python3 simple_geocoder.py --input_file=filename.csv --output_file=output.csv --api_key=XXXXXX
def parse_args():
  parser = argparse.ArgumentParser(
    "Generate a CSV of reverse geocoded location info from CSV with `lat` and `lon` columns")
  parser.add_argument('-i', '--input_file', type=str, help="CSV file containing columns with 'lat' and 'lon' headers",
                      required=True)
  parser.add_argument('-o', '--output_file', type=str,
                      help="Name of CSV file where output containing geocoded columns will be written",
                      required=True)
  parser.add_argument('-a', '--api_key', type=str,
                      help="Google Maps API Key

  parsed_args = parser.parse_args()
  return parsed_args


def googleIndex(gvec, component):
  if len(gvec) == 0:
    return None
  addr = gvec[0]["address_components"]
  truthVec = [component in addr[mk]['types'] for mk in range(len(addr))]
  if sum(truthVec) > 0:
    return addr[truthVec.index(True)]['long_name']
  else:
    return None


def get_locations(dp, gmaps, loc_map, gm_cols):
  locdf = pd.Series()
  # dp = (i_df['lat'], i_df['lon'])
  if pd.notnull(dp[0]) and pd.notnull(dp[1]):
    if dp not in loc_map.keys():
      loc_map[dp] = gmaps.reverse_geocode(dp, language='English')
    g = loc_map[dp]
    for gm_col, df_col in gm_cols.items():
      locdf[df_col] = googleIndex(g, gm_col)

  return locdf, loc_map


# add google maps columns as null values to existing data frame and return
def prepare_df(df_long, gm_cols):
  for col in gm_cols.values():
    df_long.insert(len(df_long.columns), col, None, True)

  return df_long


def main():
  args = parse_args()

  if args.output_file:
    out_file = args.output_file
  else:
    out_file = "geocoding_output.csv"

  if args.api_key:
    apikey = args.api_key
  else:
    # read login credentials for creating gmaps client
    google_creds = "/usr/etc/hive/conf/geocoder.json"
    apikey = os.popen('cat {0} | jq -r .google'.format(google_creds)).read().strip()

  # initialize dictionary to store geocoding results during run, in case the same lat/lon shows up multiple times
  loc_map = {}
  # create geocoder API client here
  gmaps = googlemaps.Client(key=apikey)

  gm_cols = {'locality': 'city',
             'administrative_area_level_2': 'county',
             'administrative_area_level_1': 'state',
             'country': 'country'}

  # read csv from file (in same folder)
  df = pd.read_csv(args.input_file)

  # add google maps API columns to the existing dataframe and prepare for reverse geocoding
  df = prepare_df(df, gm_cols)

  # iterate through rows and add location information
  for ind in df.index:
    df_entry = df.loc[ind]
    dp = (df_entry['lat'], df_entry['lon'])
    # pass lat,lon tuple and get series in return
    # also returns dictionary of seen locations that we can store for use in this program
    # but not on disk (per Google's TOU) to reduce costs in case of repeated locations
    loc_entry, loc_map = get_locations(dp, gmaps, loc_map, gm_cols)
    # finally, add the output back in to the full data frame
    for e in loc_entry.keys():
      df.loc[ind, e] = loc_entry[e]

  # save the output to disk as a csv
  df.to_csv(out_file)


if __name__ == "__main__":
  main()