// clang-format off
// automatically generated by the FlatBuffers compiler, do not modify


#ifndef FLATBUFFERS_GENERATED_FWDIFORWARDERINTERNAL_H_
#define FLATBUFFERS_GENERATED_FWDIFORWARDERINTERNAL_H_

#include "flatbuffers/flatbuffers.h"

struct fwdinfo_1_t;

enum forwarder_internal {
  forwarder_internal_NONE = 0,
  forwarder_internal_fwdinfo_1_t = 1,
  forwarder_internal_MIN = forwarder_internal_NONE,
  forwarder_internal_MAX = forwarder_internal_fwdinfo_1_t
};

inline const char **EnumNamesforwarder_internal() {
  static const char *names[] = {
    "NONE",
    "fwdinfo_1_t",
    nullptr
  };
  return names;
}

inline const char *EnumNameforwarder_internal(forwarder_internal e) {
  const size_t index = static_cast<int>(e);
  return EnumNamesforwarder_internal()[index];
}

template<typename T> struct forwarder_internalTraits {
  static const forwarder_internal enum_value = forwarder_internal_NONE;
};

template<> struct forwarder_internalTraits<fwdinfo_1_t> {
  static const forwarder_internal enum_value = forwarder_internal_fwdinfo_1_t;
};

bool Verifyforwarder_internal(flatbuffers::Verifier &verifier, const void *obj, forwarder_internal type);
bool Verifyforwarder_internalVector(flatbuffers::Verifier &verifier, const flatbuffers::Vector<flatbuffers::Offset<void>> *values, const flatbuffers::Vector<uint8_t> *types);

struct fwdinfo_1_t FLATBUFFERS_FINAL_CLASS : private flatbuffers::Table {
  enum {
    VT_SEQ_DATA = 4,
    VT_SEQ_FWD = 6,
    VT_TS_DATA = 8,
    VT_TS_FWD = 10,
    VT_FWDIX = 12,
    VT_TEAMID = 14
  };
  uint64_t seq_data() const {
    return GetField<uint64_t>(VT_SEQ_DATA, 0);
  }
  uint64_t seq_fwd() const {
    return GetField<uint64_t>(VT_SEQ_FWD, 0);
  }
  uint64_t ts_data() const {
    return GetField<uint64_t>(VT_TS_DATA, 0);
  }
  uint64_t ts_fwd() const {
    return GetField<uint64_t>(VT_TS_FWD, 0);
  }
  uint32_t fwdix() const {
    return GetField<uint32_t>(VT_FWDIX, 0);
  }
  uint64_t teamid() const {
    return GetField<uint64_t>(VT_TEAMID, 0);
  }
  bool Verify(flatbuffers::Verifier &verifier) const {
    return VerifyTableStart(verifier) &&
           VerifyField<uint64_t>(verifier, VT_SEQ_DATA) &&
           VerifyField<uint64_t>(verifier, VT_SEQ_FWD) &&
           VerifyField<uint64_t>(verifier, VT_TS_DATA) &&
           VerifyField<uint64_t>(verifier, VT_TS_FWD) &&
           VerifyField<uint32_t>(verifier, VT_FWDIX) &&
           VerifyField<uint64_t>(verifier, VT_TEAMID) &&
           verifier.EndTable();
  }
};

struct fwdinfo_1_tBuilder {
  flatbuffers::FlatBufferBuilder &fbb_;
  flatbuffers::uoffset_t start_;
  void add_seq_data(uint64_t seq_data) {
    fbb_.AddElement<uint64_t>(fwdinfo_1_t::VT_SEQ_DATA, seq_data, 0);
  }
  void add_seq_fwd(uint64_t seq_fwd) {
    fbb_.AddElement<uint64_t>(fwdinfo_1_t::VT_SEQ_FWD, seq_fwd, 0);
  }
  void add_ts_data(uint64_t ts_data) {
    fbb_.AddElement<uint64_t>(fwdinfo_1_t::VT_TS_DATA, ts_data, 0);
  }
  void add_ts_fwd(uint64_t ts_fwd) {
    fbb_.AddElement<uint64_t>(fwdinfo_1_t::VT_TS_FWD, ts_fwd, 0);
  }
  void add_fwdix(uint32_t fwdix) {
    fbb_.AddElement<uint32_t>(fwdinfo_1_t::VT_FWDIX, fwdix, 0);
  }
  void add_teamid(uint64_t teamid) {
    fbb_.AddElement<uint64_t>(fwdinfo_1_t::VT_TEAMID, teamid, 0);
  }
  fwdinfo_1_tBuilder(flatbuffers::FlatBufferBuilder &_fbb)
        : fbb_(_fbb) {
    start_ = fbb_.StartTable();
  }
  fwdinfo_1_tBuilder &operator=(const fwdinfo_1_tBuilder &);
  flatbuffers::Offset<fwdinfo_1_t> Finish() {
    const auto end = fbb_.EndTable(start_, 6);
    auto o = flatbuffers::Offset<fwdinfo_1_t>(end);
    return o;
  }
};

inline flatbuffers::Offset<fwdinfo_1_t> Createfwdinfo_1_t(
    flatbuffers::FlatBufferBuilder &_fbb,
    uint64_t seq_data = 0,
    uint64_t seq_fwd = 0,
    uint64_t ts_data = 0,
    uint64_t ts_fwd = 0,
    uint32_t fwdix = 0,
    uint64_t teamid = 0) {
  fwdinfo_1_tBuilder builder_(_fbb);
  builder_.add_teamid(teamid);
  builder_.add_ts_fwd(ts_fwd);
  builder_.add_ts_data(ts_data);
  builder_.add_seq_fwd(seq_fwd);
  builder_.add_seq_data(seq_data);
  builder_.add_fwdix(fwdix);
  return builder_.Finish();
}

inline bool Verifyforwarder_internal(flatbuffers::Verifier &verifier, const void *obj, forwarder_internal type) {
  switch (type) {
    case forwarder_internal_NONE: {
      return true;
    }
    case forwarder_internal_fwdinfo_1_t: {
      auto ptr = reinterpret_cast<const fwdinfo_1_t *>(obj);
      return verifier.VerifyTable(ptr);
    }
    default: return false;
  }
}

inline bool Verifyforwarder_internalVector(flatbuffers::Verifier &verifier, const flatbuffers::Vector<flatbuffers::Offset<void>> *values, const flatbuffers::Vector<uint8_t> *types) {
  if (values->size() != types->size()) return false;
  for (flatbuffers::uoffset_t i = 0; i < values->size(); ++i) {
    if (!Verifyforwarder_internal(
        verifier,  values->Get(i), types->GetEnum<forwarder_internal>(i))) {
      return false;
    }
  }
  return true;
}

#endif  // FLATBUFFERS_GENERATED_FWDIFORWARDERINTERNAL_H_
// clang-format on
