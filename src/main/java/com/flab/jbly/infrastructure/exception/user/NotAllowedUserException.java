package com.flab.jbly.infrastructure.exception.user;

import com.flab.jbly.infrastructure.exception.ErrorCode;
import lombok.Getter;

@Getter
public class NotAllowedUserException extends IllegalArgumentException {

    private ErrorCode errorCode;

    public NotAllowedUserException(String message, ErrorCode errorCode) {
        super(message);
        this.errorCode = errorCode;
    }
}
