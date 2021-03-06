# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: slam_proto.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='slam_proto.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x10slam_proto.proto\"[\n\x07SlamMap\x12\t\n\x01x\x18\x01 \x01(\x01\x12\t\n\x01y\x18\x02 \x01(\x01\x12\r\n\x05theta\x18\x03 \x01(\x01\x12\x0e\n\x06height\x18\x04 \x01(\x05\x12\r\n\x05width\x18\x05 \x01(\x05\x12\x0c\n\x04grid\x18\x06 \x03(\x05\x62\x06proto3')
)




_SLAMMAP = _descriptor.Descriptor(
  name='SlamMap',
  full_name='SlamMap',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='x', full_name='SlamMap.x', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='y', full_name='SlamMap.y', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='theta', full_name='SlamMap.theta', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='height', full_name='SlamMap.height', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='width', full_name='SlamMap.width', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='grid', full_name='SlamMap.grid', index=5,
      number=6, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=20,
  serialized_end=111,
)

DESCRIPTOR.message_types_by_name['SlamMap'] = _SLAMMAP
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SlamMap = _reflection.GeneratedProtocolMessageType('SlamMap', (_message.Message,), dict(
  DESCRIPTOR = _SLAMMAP,
  __module__ = 'slam_proto_pb2'
  # @@protoc_insertion_point(class_scope:SlamMap)
  ))
_sym_db.RegisterMessage(SlamMap)


# @@protoc_insertion_point(module_scope)
