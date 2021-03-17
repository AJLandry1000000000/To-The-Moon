import { useState } from "react";
import { Button, Form } from "react-bootstrap";
import { connect } from "react-redux";
import ClipLoader from "react-spinners/ClipLoader";
import portfolioActions from "../redux/actions/portfolioActions";

interface CreatePortfolioFormParams {
  name: string;
}

interface CreatePortfolioState {
  values: CreatePortfolioFormParams;
  errors: CreatePortfolioFormParams;
}

interface StateProps {
  createPortfolioForm: CreatePortfolioState;
  isLoading: boolean;
  error: Object;
  token: string;
}

interface DispatchProps {
  submitForm: (payload: CreatePortfolioFormParams) => void;
  createPortfolio: (payload: CreatePortfolioFormParams) => void;
}

const CreatePortfolioForm: React.FC<StateProps & DispatchProps> = (props) => {
  const {
    createPortfolioForm,
    isLoading,
    token,
    error,
    submitForm,
    createPortfolio,
  } = props;
  // purposely input dummy data
  const [name, setName] = useState("");

  const onSubmit = (e: any) => {
    e.preventDefault();
    createPortfolio({ name });
  };

  const onBlur = () => {
    submitForm({ name });
  };

  const formComponent = (
    <Form onSubmit={(e) => onSubmit(e)}>
      <Form.Group controlId="formBasicName">
        <Form.Label>Name</Form.Label>
        <Form.Control
          type="text"
          placeholder="Enter name"
          isInvalid={createPortfolioForm.errors.name.length > 0}
          isValid={
            !!createPortfolioForm.values.name &&
            createPortfolioForm.errors.name.length === 0
          }
          onChange={(e) => setName(e.target.value)}
          onBlur={onBlur}
        />
        <Form.Control.Feedback type="invalid">
          {createPortfolioForm.errors.name}
        </Form.Control.Feedback>
        <Form.Text className="text-muted">
          Choose a unique portfolio name.
        </Form.Text>
      </Form.Group>

      <Button variant="primary" type="submit">
        Create Portfolio
      </Button>
    </Form>
  );

  const loadingSpinnerComponent = (
    <div>
      <ClipLoader color={"green"} loading={isLoading} />
      <h5>Preparing rocket fuel...</h5>
    </div>
  );

  return isLoading ? loadingSpinnerComponent : formComponent;
};

const mapStateToProps = (state: any) => ({
  createPortfolioForm: state.submitCreatePortfolioForm.createPortfolioForm,
  isLoading: state.createPortfolio.createPortfolio.loading,
  token: state.createPortfolio.createPortfolio.token,
  error: state.createPortfolio.createPortfolio.error,
});

const mapDispatchToProps = (dispatch: any) => {
  return {
    submitForm: (formPayload: CreatePortfolioFormParams) => {
      dispatch(portfolioActions.submitCreatePortfolioForm(formPayload));
    },
    createPortfolio: (formPayload: CreatePortfolioFormParams) => {
      dispatch(portfolioActions.createPortfolio(formPayload));
    },
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(CreatePortfolioForm);