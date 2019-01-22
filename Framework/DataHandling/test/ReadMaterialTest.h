// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2009 ISIS Rutherford Appleton Laboratory UKRI,
//     NScD Oak Ridge National Laboratory, European Spallation Source
//     & Institut Laue - Langevin
// SPDX - License - Identifier: GPL - 3.0 +
#include "MantidDataHandling/ReadMaterial.h"
#include "MantidKernel/Atom.h"
#include "MantidKernel/Material.h"
#include <cxxtest/TestSuite.h>

using namespace Mantid;
using namespace Mantid::Kernel;
using namespace Mantid::DataHandling;

class ReadMaterialTest : public CxxTest::TestSuite {
public:
  static ReadMaterialTest *createSuite() { return new ReadMaterialTest(); }
  static void destroySuite(ReadMaterialTest *suite) { delete suite; }

  void testSuccessfullValidateInputsFormula() {
    const ReadMaterial::MaterialParameters params = [this]() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.chemicalSymbol = FORMULA;
      setMaterial.atomicNumber = 0;
      setMaterial.massNumber = 0;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT(result.empty());
  }

  void testSuccessfullValidateInputsAtomicNumber() {
    const ReadMaterial::MaterialParameters params = []() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.atomicNumber = 1;
      setMaterial.massNumber = 1;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT(result.empty());
  }

  void testFailureValidateInputsFormulaPlusAtomicNumber() {
    const ReadMaterial::MaterialParameters params = [this]() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.chemicalSymbol = FORMULA;
      setMaterial.atomicNumber = 1;
      setMaterial.massNumber = 1;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT_EQUALS(result["AtomicNumber"],
                     "Cannot specify both ChemicalFormula and AtomicNumber")
  }

  void testFailureValidateInputsNoMaterial() {
    const ReadMaterial::MaterialParameters params = []() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.atomicNumber = 0;
      setMaterial.massNumber = 0;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT_EQUALS(result["ChemicalFormula"], "Need to specify the material")
  }

  void testSuccessfullValidateInputsSampleNumber() {
    const ReadMaterial::MaterialParameters params = []() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.atomicNumber = 1;
      setMaterial.massNumber = 1;
      setMaterial.sampleNumberDensity = 1;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT(result.empty());
  }

  void testSuccessfullValidateInputsZParam() {
    const ReadMaterial::MaterialParameters params = []() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.atomicNumber = 1;
      setMaterial.massNumber = 1;
      setMaterial.zParameter = 1;
      setMaterial.unitCellVolume = 1;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT(result.empty());
  }

  void testSuccessfullValidateInputsSampleMass() {
    const ReadMaterial::MaterialParameters params = []() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.atomicNumber = 1;
      setMaterial.massNumber = 1;
      setMaterial.sampleMassDensity = 1;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT(result.empty());
  }

  void testFailureValidateInputsSampleNumberAndZParam() {
    const ReadMaterial::MaterialParameters params = []() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.atomicNumber = 1;
      setMaterial.massNumber = 1;
      setMaterial.sampleNumberDensity = 1;
      setMaterial.zParameter = 1;
      setMaterial.unitCellVolume = 1;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT_EQUALS(result["ZParameter"],
                     "Can not give ZParameter with SampleNumberDensity set")
  }

  void testFailureValidateInputsZParamWithSampleMass() {
    const ReadMaterial::MaterialParameters params = []() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.atomicNumber = 1;
      setMaterial.massNumber = 1;
      setMaterial.zParameter = 1;
      setMaterial.unitCellVolume = 1;
      setMaterial.sampleMassDensity = 1;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT_EQUALS(result["SampleMassDensity"],
                     "Can not give SampleMassDensity with ZParameter set")
  }

  void testFailureValidateInputsZParamWithoutUnitCell() {
    const ReadMaterial::MaterialParameters params = []() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.atomicNumber = 1;
      setMaterial.massNumber = 1;
      setMaterial.zParameter = 1;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT_EQUALS(result["UnitCellVolume"],
                     "UnitCellVolume must be provided with ZParameter")
  }

  void testFailureValidateInputsSampleNumWithSampleMass() {
    const ReadMaterial::MaterialParameters params = []() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.atomicNumber = 1;
      setMaterial.massNumber = 1;
      setMaterial.sampleNumberDensity = 1;
      setMaterial.sampleMassDensity = 1;
      return setMaterial;
    }
    ();

    auto result = ReadMaterial::validateInputs(params);

    TS_ASSERT_EQUALS(
        result["SampleMassDensity"],
        "Can not give SampleMassDensity with SampleNumberDensity set")
  }

  void testMaterialIsCorrect() {
    const ReadMaterial::MaterialParameters params = [this]() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.chemicalSymbol = FORMULA;
      setMaterial.sampleNumberDensity = 1;
      setMaterial.coherentXSection = 1;
      setMaterial.incoherentXSection = 2;
      setMaterial.attenuationXSection = 3;
      setMaterial.scatteringXSection = 4;
      return setMaterial;
    }
    ();

    ReadMaterial reader;
    reader.setMaterialParameters(params);
    auto material = reader.buildMaterial();

    Kernel::MaterialBuilder builder;
    builder.setFormula(FORMULA);
    builder.setNumberDensity(1);
    builder.setCoherentXSection(1);
    builder.setIncoherentXSection(2);
    builder.setAbsorptionXSection(3);
    builder.setTotalScatterXSection(4);
    auto check = builder.build();

    compareMaterial(*material, check);
  }

  void testGenerateScatteringInfo() {
    const ReadMaterial::MaterialParameters params = [this]() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.chemicalSymbol = FORMULA;
      setMaterial.sampleNumberDensity = 1;
      return setMaterial;
    }
    ();

    ReadMaterial reader;
    reader.setMaterialParameters(params);
    auto material = reader.buildMaterial();

    Kernel::MaterialBuilder builder;
    builder.setFormula(FORMULA);
    builder.setNumberDensity(1);
    builder.setCoherentXSection(0.0184000000);
    builder.setIncoherentXSection(5.0800000022);
    builder.setAbsorptionXSection(5.0800000022);
    builder.setTotalScatterXSection(5.1000000044);
    auto check = builder.build();

    compareMaterial(*material, check);
  }

  void testNoMaterialFailure() {
    const ReadMaterial::MaterialParameters params = [this]() -> auto {
      ReadMaterial::MaterialParameters setMaterial;
      setMaterial.chemicalSymbol = EMPTY;
      setMaterial.atomicNumber = 0;
      setMaterial.massNumber = 0;
      setMaterial.sampleNumberDensity = 1;
      setMaterial.zParameter = EMPTY_DOUBLE_VAL;
      setMaterial.unitCellVolume = EMPTY_DOUBLE_VAL;
      setMaterial.sampleMassDensity = EMPTY_DOUBLE_VAL;
      return setMaterial;
    }
    ();

    ReadMaterial reader;
    reader.setMaterialParameters(params);
    TS_ASSERT_THROWS(reader.buildMaterial(), std::runtime_error);
  }

private:
  const double EMPTY_DOUBLE_VAL = 8.9884656743115785e+307;
  const double PRECISION = 1e-8;
  const std::string EMPTY = "";
  const std::string FORMULA = "V";

  void compareMaterial(const Material &material, const Material &check) {
    std::vector<Material::FormulaUnit> checkFormula = check.chemicalFormula();
    std::vector<Material::FormulaUnit> materialFormula =
        material.chemicalFormula();

    TS_ASSERT_EQUALS(material.numberDensity(), check.numberDensity());
    TS_ASSERT_DELTA(material.cohScatterXSection(), check.cohScatterXSection(),
                    PRECISION);
    TS_ASSERT_DELTA(material.incohScatterXSection(),
                    check.incohScatterXSection(), PRECISION);
    TS_ASSERT_DELTA(material.absorbXSection(), check.absorbXSection(),
                    PRECISION);
    TS_ASSERT_DELTA(material.totalScatterXSection(),
                    check.totalScatterXSection(), PRECISION);
    TS_ASSERT_EQUALS(checkFormula[0].multiplicity,
                     materialFormula[0].multiplicity);
    TS_ASSERT_EQUALS(checkFormula.size(), materialFormula.size())
  }
};
