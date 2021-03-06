
from dataclasses import InitVar, dataclass, field
from typing import Dict

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


def hv_selection(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if other_table_refs[0] == "LHV":
        return target_table_ref[row_key][extra["LHV"]]
    elif other_table_refs[0] == "HHV":
        return target_table_ref[row_key][extra["HHV"]]


def hv_ratio(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    return target_table_ref[row_key][extra["LHV"]] / target_table_ref[row_key][extra["HHV"]]


def s_ratio(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return target_table_ref[row_key]["S ratio, (ppm by wt)"]/1000000


def fill_gwp_selection(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if other_table_refs == 100:
        return target_table_ref[row_key]["100 year GWP"]
    elif other_table_refs == 20:
        return target_table_ref[row_key]["20 year GWP"]


@dataclass
class Constants:

    def __post_init__(self, user_input):
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")
        fill_calculated_cells(target_table_ref=self.table_3_fuel_specifications_liquid_fuels,
                              func_to_apply=hv_selection, included_cols=[
                                  "User Selection: LHV or HHV, Btu/gal"], other_table_refs=[self.hv],
                              # hacked the keymap to get around the different units in the HV keys
                              # so I can reuse the hv_selection function
                              extra={'LHV': "LHV, Btu/gal", 'HHV': "HHV, Btu/gal"})

        fill_calculated_cells(target_table_ref=self.table_3_fuel_specifications_gaseous_fuels,
                              func_to_apply=hv_selection, included_cols=[
                                  "User Selection: LHV or HHV, Btu/ft3"], other_table_refs=[self.hv],
                              # hacked the keymap to get around the different units in the HV keys
                              # so I can reuse the hv_selection function
                              extra={'LHV': "LHV, Btu/ft3", 'HHV': "HHV, Btu/ft3"})

        fill_calculated_cells(target_table_ref=self.table_3_fuel_specifications_solid_fuels,
                              func_to_apply=hv_selection, included_cols=[
                                  "User Selection: LHV or HHV, Btu/ton"], other_table_refs=[self.hv],
                              # hacked the keymap to get around the different units in the HV keys
                              # so I can reuse the hv_selection function
                              extra={'LHV': "LHV, Btu/ton", 'HHV': "HHV, Btu/ton"})

        fill_calculated_cells(target_table_ref=self.table_3_fuel_specifications_liquid_fuels,
                              func_to_apply=s_ratio, included_cols=[
                                  "S ratio, Actual ratio by wt"])
        fill_calculated_cells(target_table_ref=self.table_3_fuel_specifications_solid_fuels,
                              func_to_apply=s_ratio, included_cols=[
                                  "S ratio, Actual ratio by wt"])
        fill_calculated_cells(target_table_ref=self.table_3_fuel_specifications_gaseous_fuels,
                              func_to_apply=s_ratio, included_cols=[
                                  "S ratio, Actual ratio by wt"])

        fill_calculated_cells(target_table_ref=self.table_3_fuel_specifications_liquid_fuels,
                              func_to_apply=hv_ratio, included_cols=[
                                  "LHV/HHV"],
                              # hacked the keymap to get around the different units in the HV keys
                              # so I can reuse the hv_ratio function
                              extra={'LHV': "LHV, Btu/gal", 'HHV': "HHV, Btu/gal"})

        fill_calculated_cells(target_table_ref=self.table_3_fuel_specifications_gaseous_fuels,
                              func_to_apply=hv_ratio, included_cols=[
                                  "LHV/HHV"],
                              # hacked the keymap to get around the different units in the HV keys
                              # so I can reuse the hv_ratio function
                              extra={'LHV': "LHV, Btu/ft3", 'HHV': "HHV, Btu/ft3"})

        fill_calculated_cells(target_table_ref=self.table_3_fuel_specifications_solid_fuels,
                              func_to_apply=hv_ratio, included_cols=[
                                  "LHV/HHV"],
                              # hacked the keymap to get around the different units in the HV keys
                              # so I can reuse the hv_ratio function
                              extra={'LHV': "LHV, Btu/ton", 'HHV': "HHV, Btu/ton"})

        fill_calculated_cells(target_table_ref=self.table_1_gwp,
                              func_to_apply=fill_gwp_selection, included_cols=[
                                  "User Selection"],
                                  other_table_refs=self.GWP)

    user_input: InitVar[Dict] = {}

    # Constants sheet, table: User Selection, LHV or HHV
    # USER_INPUT
    hv: str = "LHV"

    # Constants sheet, table: User Selection, 100 or 20 (yr GWP)
    # USER_INPUT
    GWP: int = 100

    # Constants sheet, table: Table 1: Hundred-Year Global Warming Potentials
    # STATIC
    table_1_gwp: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Table_1_Global_Warming_Potentials', 'constants'))

    # Constants sheet, table: Table 2: Conversion Factors
    # NOTE: I CHANGED THE ORDER OF COLUMNS from the Excel workbook (unit, factor)
    # STATIC
    table_2_conversion_factors: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Table_2_Conversion_Factors', 'constants'))

    # Constants sheet, table: Table 3: Table 3- Fuel Specifications -- Liquid Fuels
    # STATIC
    # CALCULATED
    # USER INPUT
    table_3_fuel_specifications_liquid_fuels: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Table_3_Fuel_Specifications_Liquid_Fuels', 'constants'))

    # Constants sheet, table: Table 3: Table 3- Fuel Specifications -- Gaseous Fuels (at 32F and 1atm)
    # STATIC
    # CALCULATED
    table_3_fuel_specifications_gaseous_fuels: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Table_3_Fuel_Specifications_Gaseous_Fuels', 'constants'))

    # Constants sheet, table: Table 3: Table 3- Fuel Specifications -- Solid Fuels
    # STATIC
    # CALCULATED
    table_3_fuel_specifications_solid_fuels: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Table_3_Fuel_Specifications_Solid_Fuels', 'constants'))

    # Constants sheet, table: Table 4- Carbon and Sulfur Ratios of Pollutants
    # STATIC
    table_4_carbon_and_sulfer_ratios: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Table_4_Carbon_and_Sulfur_Ratios_of_Pollutants', 'constants'))

    # Constants sheet, table: Table 5: Solid Fuel Densities
    # STATIC
    table_5_solid_fuel_densities: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Table_5_Solid_Fuel_Densities', 'constants'))

    # Constants sheet, table: Table 5: Solid Fuel Densities
    # STATIC
    table_6_boe_conversions: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Table_6_BOE_Conversions', 'constants'))
