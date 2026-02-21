import cocotb
from cocotb.triggers import Timer
from model import get_8bit_op, to_binary, to_float


@cocotb.test()
async def test_all_inputs(dut):
    """Test all possible pairs of 8-bit inputs."""

    async def store(operand, half, data):
        val = 0
        val |= (0 << 0) # clock
        val |= (0 << 1) # ctrl0
        val |= (operand << 2) # ctrl1
        val |= (half << 3) # ctrl2
        for i in range(4):
            val |= (data[i] << (4+i))
        dut.io_in.value = val
        await Timer(1, units="ms")
        val |= (1 << 0) # clock high
        dut.io_in.value = val
        await Timer(1, units="ms")

    fp8_mul_model = get_8bit_op(lambda a, b: a * b)

    # TODO: Test in random order
    for i in range(256):
        for j in range(256):
            in1 = to_binary(i)
            in2 = to_binary(j)
            await store(0, 0, in1[:4])
            await store(0, 1, in1[4:])
            await store(1, 0, in2[:4])
            await store(1, 1, in2[4:])
            correct = fp8_mul_model(i, j)
            assert str(dut.io_out.value) == f"{correct:08b}", f"{to_float(i)} ({i:08b}) * {to_float(j)} ({j:08b}) = {to_float(dut.io_out.value.integer)} ({dut.io_out.value.integer:08b}), should be {to_float(correct)} ({correct:08b})"
