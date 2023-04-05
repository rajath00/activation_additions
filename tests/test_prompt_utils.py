""" Tests for the prompt_utils module. """

from transformer_lens.HookedTransformer import HookedTransformer

from algebraic_value_editing.prompt_utils import RichPrompt
from algebraic_value_editing import prompt_utils


model: HookedTransformer = HookedTransformer.from_pretrained(
    model_name="attn-only-1l"
)


def test_creation():
    """Test that we can create a RichPrompt."""
    rich_prompt = RichPrompt(
        prompt="Hello world!",
        act_name="encoder",
        coeff=1.0,
    )
    assert rich_prompt.prompt == "Hello world!"
    assert rich_prompt.act_name == "encoder"
    assert rich_prompt.coeff == 1.0


def test_x_vector_creation():
    """Test that we can create a RichPrompt's x_vector."""
    rich_prompt_positive = RichPrompt(
        prompt="Hello world!", act_name="", coeff=1.0
    )
    rich_prompt_negative = RichPrompt(
        prompt="Goodbye world!", act_name="", coeff=-1.0
    )

    x_vector_positive, x_vector_negative = prompt_utils.get_x_vector(
        prompt1="Hello world!",
        prompt2="Goodbye world!",
        coeff=1.0,
        act_name="",
    )

    # Check that the x_vectors are the same as the RichPrompts
    for xvec, rch_prompt in zip(
        [x_vector_positive, x_vector_negative],
        [rich_prompt_positive, rich_prompt_negative],
    ):
        assert xvec.prompt == rch_prompt.prompt
        assert xvec.act_name == rch_prompt.act_name
        assert xvec.coeff == rch_prompt.coeff


def test_x_vector_right_pad():
    """Test that we can right pad the x_vector."""
    prompt1 = "Hello world fdsa dfsa fsad!"
    xv_pos, xv_neg = prompt_utils.get_x_vector(
        prompt1=prompt1,
        prompt2="Goodbye world!",
        coeff=1.0,
        act_name="",
        pad_method="tokens_right",
        model=model,
    )

    assert xv_pos.tokens.shape == xv_neg.tokens.shape, "Padding failed."
    assert (
        model.to_string(xv_neg.tokens[-1]) == "<|PAD|>"
    ), "Padded with incorrect token."

    xv_pos_prompt = model.to_string(xv_pos.tokens)
    assert xv_pos_prompt == prompt1, "Accidentally padded the longer string."
