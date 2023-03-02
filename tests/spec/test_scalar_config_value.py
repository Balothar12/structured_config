
from typing import Any, List, Tuple, Type
from dataclasses import dataclass, field
import pytest
import structured_config

class TestScalarConfigValue:

    @dataclass
    class ConvertedScalarValue:
        type: Type
        value: Any

    @dataclass
    class ScalarConfigData:
        value: Any
        type: Type
        other_types: List[Type] = field(default_factory=lambda: [])

        def __post_init__(self):
            self.other_types = list(filter(lambda t: self.type != t, TestScalarConfigValue.types))

        def make_others(self):
            return [t() for t in self.other_types]

    class Converter(structured_config.ConverterBase):
        def convert(self, other: structured_config.ConversionSourceType) -> structured_config.ConversionTargetType:
            return TestScalarConfigValue.ConvertedScalarValue(type=type(other), value=other)

    class ConfigValidator(structured_config.ValidatorBase):
        def __init__(self, expected):
            self.expected = expected
            self.validated = 0
        def validate(self, data: structured_config.ValidatorSourceType) -> bool:
            self.validated += 1
            return data == self.expected.value and type(data) is self.expected.type

    class ConvertedValidator(structured_config.ValidatorBase):
        def __init__(self, expected):
            self.expected = expected
            self.validated = 0
        def validate(self, data: structured_config.ValidatorSourceType) -> bool:
            self.validated += 1
            return type(data) is TestScalarConfigValue.ConvertedScalarValue and data.value == self.expected.value and data.type is self.expected.type

    values: List[Any] = ["test-str", 123, 123.456, True, False]
    types: List[Type] = [str, int, float, bool, bool]

    @pytest.fixture
    def converter(self) -> Converter:
        return TestScalarConfigValue.Converter()

    @pytest.fixture
    def data_with_pre_validator(self, data) -> Tuple[ScalarConfigData, ConfigValidator]:
        return (data, TestScalarConfigValue.ConfigValidator(expected=data))

    @pytest.fixture
    def data_with_post_validator(self, data) -> Tuple[ScalarConfigData, ConvertedValidator]:
        return (data, TestScalarConfigValue.ConvertedValidator(expected=data))

    @pytest.fixture(params=list(zip(values, types)))
    def data(self, request) -> ScalarConfigData:
        value, type = request.param

        return TestScalarConfigValue.ScalarConfigData(value=value, type=type)
    
    @pytest.fixture
    def for_passthrough(self, data) -> Tuple[ScalarConfigData, structured_config.ScalarConfigValue]:
        return (
            data,
            structured_config.ScalarConfigValue(
                config_type_check=structured_config.RequireConfigType.none(),
                converted_type_check=structured_config.RequireConvertedType.none(),
                converter=structured_config.NoOpConverter(),
                validator=structured_config.PassAllValidator(),
                validator_phase=structured_config.ValidatorPhase.NoValidation,
                required=True,
                default=None,
            )
        )

    @pytest.fixture
    def for_passthrough_optional(self, data) -> Tuple[ScalarConfigData, structured_config.ScalarConfigValue]: 
        return (
            data,
            structured_config.ScalarConfigValue(
                config_type_check=structured_config.RequireConfigType.none(),
                converted_type_check=structured_config.RequireConvertedType.none(),
                converter=structured_config.NoOpConverter(),
                validator=structured_config.PassAllValidator(),
                validator_phase=structured_config.ValidatorPhase.NoValidation,
                required=False,
                default=data.value,
            )
        )
    
    @pytest.fixture
    def for_conversion(self, data, converter) -> Tuple[ScalarConfigData, structured_config.ScalarConfigValue]:
        return (
            data,
            structured_config.ScalarConfigValue(
                config_type_check=structured_config.RequireConfigType.none(),
                converted_type_check=structured_config.RequireConvertedType.none(),
                converter=converter,
                validator=structured_config.PassAllValidator(),
                validator_phase=structured_config.ValidatorPhase.NoValidation,
                required=True,
                default=None,
            )
        )
    
    @pytest.fixture
    def for_pre_validation(self, data_with_pre_validator) -> Tuple[ScalarConfigData, ConfigValidator, structured_config.ScalarConfigValue]:
        data, validator = data_with_pre_validator
        return (
            data,
            validator,
            structured_config.ScalarConfigValue(
                config_type_check=structured_config.RequireConfigType.none(),
                converted_type_check=structured_config.RequireConvertedType.none(),
                converter=structured_config.NoOpConverter(),
                validator=validator,
                validator_phase=structured_config.ValidatorPhase.BeforeConversion,
                required=True,
                default=None,
            )
        )
    
    @pytest.fixture
    def for_post_validation(self, data_with_post_validator, converter) -> Tuple[ScalarConfigData, ConvertedValidator, structured_config.ScalarConfigValue]:
        data, validator = data_with_post_validator
        return (
            data,
            validator,
            structured_config.ScalarConfigValue(
                config_type_check=structured_config.RequireConfigType.none(),
                converted_type_check=structured_config.RequireConvertedType.none(),
                converter=converter,
                validator=validator,
                validator_phase=structured_config.ValidatorPhase.AfterConversion,
                required=True,
                default=None,
            )
        )
    
    @pytest.fixture
    def with_config_typecheck(self, data) -> Tuple[ScalarConfigData, structured_config.ScalarConfigValue]:
        return (
            data,
            structured_config.ScalarConfigValue(
                config_type_check=structured_config.RequireConfigType.from_type_list([data.type]),
                converted_type_check=structured_config.RequireConvertedType.none(),
                converter=structured_config.NoOpConverter(),
                validator=structured_config.PassAllValidator(),
                validator_phase=structured_config.ValidatorPhase.NoValidation,
                required=True,
                default=None,
            )
        )
    
    @pytest.fixture
    def with_failed_config_typecheck(self, with_config_typecheck) -> Tuple[List[Any], structured_config.ScalarConfigValue]:
        data, value = with_config_typecheck
        return (
            data.make_others(),
            value
        )
    
    @pytest.fixture
    def with_converted_typecheck(self, data: ScalarConfigData, converter) -> Tuple[ScalarConfigData, structured_config.ScalarConfigValue]:
        return (
            data,
            structured_config.ScalarConfigValue(
                config_type_check=structured_config.RequireConfigType.none(),
                converted_type_check=structured_config.RequireConvertedType.from_type_list([TestScalarConfigValue.ConvertedScalarValue]),
                converter=converter,
                validator=structured_config.PassAllValidator(),
                validator_phase=structured_config.ValidatorPhase.NoValidation,
                required=True,
                default=None,
            )
        )
    
    @pytest.fixture
    def with_failed_converted_typecheck(self, data) -> Tuple[ScalarConfigData, structured_config.ScalarConfigValue]:
        return (
            data,
            structured_config.ScalarConfigValue(
                config_type_check=structured_config.RequireConfigType.none(),
                converted_type_check=structured_config.RequireConvertedType.from_type_list([TestScalarConfigValue.ConvertedScalarValue]),
                converter=structured_config.NoOpConverter(),
                validator=structured_config.PassAllValidator(),
                validator_phase=structured_config.ValidatorPhase.NoValidation,
                required=True,
                default=None,
            )
        )


    def test_variable_passthrough(self, for_passthrough):
        data, value = for_passthrough
        result = value.convert(data.value)
        assert result == data.value
        assert type(result) is data.type

    def test_type_check_accepted(self, with_config_typecheck):
        data, value = with_config_typecheck
        result = value.convert(data.value)
        assert result == data.value
        assert type(result) is data.type

    def test_type_check_failed(self, with_failed_config_typecheck):
        data, value = with_failed_config_typecheck
        for fail in data:
            with pytest.raises(TypeError):
                result = value.convert(fail)

    def test_conversion(self, for_conversion): 
        data, value = for_conversion
        result = value.convert(data.value)
        assert type(result) is TestScalarConfigValue.ConvertedScalarValue
        assert result.value == data.value
        assert result.type == data.type


    def test_converted_type_check_accepted(self, with_converted_typecheck): 
        data, value = with_converted_typecheck
        result = value.convert(data.value)
        assert type(result) is TestScalarConfigValue.ConvertedScalarValue
        assert result.value == data.value
        assert result.type == data.type

    def test_converted_type_check_failed(self, with_failed_converted_typecheck):
        fail, value = with_failed_converted_typecheck
        with pytest.raises(TypeError):
            result = value.convert(fail)

    def test_validation_before_conversion(self, for_pre_validation):
        data, validator, value = for_pre_validation
        result = value.convert(data.value)
        assert result == data.value
        assert type(result) is data.type
        assert validator.validated == 1

    def test_validation_after_conversion(self, for_post_validation):
        data, validator, value = for_post_validation
        result = value.convert(data.value)
        assert type(result) is TestScalarConfigValue.ConvertedScalarValue
        assert result.value == data.value
        assert result.type == data.type
        assert validator.validated == 1
        
    def test_fail_required_nonexistent_value(self, for_passthrough): 
        data, value = for_passthrough
        with pytest.raises(structured_config.RequiredValueNotFoundException):
            result = value.convert(None)

    def test_pass_required_specified_value(self, for_passthrough):
        data, value = for_passthrough
        result = value.convert(data.value)
        assert result == data.value
        assert type(result) is data.type

    def test_pass_optional_nonexistent_value(self, for_passthrough_optional):
        data, value = for_passthrough_optional
        result = value.convert(None)
        assert result == data.value
        assert type(result) is data.type

    def test_pass_optional_specified_value(self, for_passthrough_optional):
        data, value = for_passthrough_optional
        result = value.convert(data.value)
        assert result == data.value
        assert type(result) is data.type